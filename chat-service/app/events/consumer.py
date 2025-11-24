# chat-service/app/events/consumer.py
import os
import json
import uuid
import logging
from datetime import datetime
import pika
from sqlmodel import Session, create_engine, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models.user_snapshot import UserSnapshot, ProcessedEvent

logger = logging.getLogger(__name__)

DB_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@db:5432/chatdb")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/%2f")
EXCHANGE = "user.events"
QUEUE = "chat.user-snapshots"
DLX = "user.events.dlx"
DLQ = "chat.user-snapshots.dlq"

engine = create_engine(DB_URL, echo=False, pool_pre_ping=True)

class UserEventConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self._setup_rabbitmq()

    def _setup_rabbitmq(self):
        params = pika.URLParameters(RABBITMQ_URL)
        params.heartbeat = 600
        params.blocked_connection_timeout = 300
        
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        
        # Declare exchanges
        self.channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
        self.channel.exchange_declare(exchange=DLX, exchange_type="fanout", durable=True)
        
        # Dead letter queue
        self.channel.queue_declare(queue=DLQ, durable=True)
        self.channel.queue_bind(queue=DLQ, exchange=DLX)
        
        # Main queue with DLX
        self.channel.queue_declare(
            queue=QUEUE,
            durable=True,
            arguments={"x-dead-letter-exchange": DLX}
        )
        self.channel.queue_bind(queue=QUEUE, exchange=EXCHANGE, routing_key="user.v1.*")
        
        # QoS
        self.channel.basic_qos(prefetch_count=50)

    def _upsert_user_snapshot(self, session: Session, data: dict):
        """Upsert user snapshot using PostgreSQL ON CONFLICT"""
        user_id = uuid.UUID(data["user_id"])
        
        stmt = pg_insert(UserSnapshot.__table__).values(
            user_id=user_id,
            username=data["username"],
            email=data.get("email", ""),
            name=data["name"],
            is_active=data.get("is_active", True),
            role=data.get("role", "user"),
            updated_at=datetime.utcnow()
        )
        
        stmt = stmt.on_conflict_do_update(
            index_elements=[UserSnapshot.__table__.c.user_id],
            set_={
                "username": stmt.excluded.username,
                "email": stmt.excluded.email,
                "name": stmt.excluded.name,
                "is_active": stmt.excluded.is_active,
                "role": stmt.excluded.role,
                "updated_at": stmt.excluded.updated_at,
            }
        )
        
        session.exec(stmt)

    def _handle_message(self, ch, method, properties, body):
        try:
            event = json.loads(body)
            event_id = event["event_id"]
            event_type = event["type"]
            data = event["data"]
            
            logger.info(f"Processing {event_type} event_id={event_id}")
            
            with Session(engine) as session:
                # Check if already processed (idempotency)
                existing = session.get(ProcessedEvent, event_id)
                if existing:
                    logger.info(f"Event {event_id} already processed, skipping")
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    return
                
                # Handle different event types
                if event_type in ("user.v1.created", "user.v1.updated"):
                    self._upsert_user_snapshot(session, data)
                
                elif event_type == "user.v1.deleted":
                    # Mark as inactive or delete
                    user_id = uuid.UUID(data["user_id"])
                    snapshot = session.get(UserSnapshot, user_id)
                    if snapshot:
                        snapshot.is_active = False
                        snapshot.updated_at = datetime.utcnow()
                        session.add(snapshot)
                
                # Mark event as processed
                session.add(ProcessedEvent(event_id=event_id, event_type=event_type))
                session.commit()
                
                logger.info(f"Successfully processed {event_type} event_id={event_id}")
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            # Send to DLQ
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start_consuming(self):
        logger.info(f"Starting consumer on queue {QUEUE}")
        self.channel.basic_consume(queue=QUEUE, on_message_callback=self._handle_message)
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()
            self.connection.close()

# Entry point
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    consumer = UserEventConsumer()
    consumer.start_consuming()