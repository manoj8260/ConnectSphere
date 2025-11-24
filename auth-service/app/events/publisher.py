# auth-service/app/events/publisher.py
import os
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any
import pika
from pika.exceptions import AMQPConnectionError
import logging

logger = logging.getLogger(__name__)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/%2f")
EXCHANGE = "user.events"

class EventPublisher:
    def __init__(self):
        self.connection = None
        self.channel = None
        self._setup_connection()

    def _setup_connection(self):
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            params.heartbeat = 600
            params.blocked_connection_timeout = 300
            
            self.connection = pika.BlockingConnection(params)
            self.channel = self.connection.channel()
            
            # Declare exchange
            self.channel.exchange_declare(
                exchange=EXCHANGE,
                exchange_type="topic",
                durable=True
            )
            
            # Enable publisher confirms
            self.channel.confirm_delivery()
            
        except AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def publish_event(self, event_type: str, data: Dict[str, Any]):
        """Publish an event to RabbitMQ"""
        event = {   
            "type": event_type,
            "event_id": str(uuid.uuid4()),
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "data": data
        }
        
        body = json.dumps(event, default=str).encode("utf-8")
        
        try:
            self.channel.basic_publish(
                exchange=EXCHANGE,
                routing_key=event_type,
                body=body,
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2,  # persistent
                    message_id=event["event_id"]
                ),
                mandatory=False
            )
            logger.info(f"Published {event_type} for event_id={event['event_id']}")
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            self._setup_connection()  # reconnect
            raise

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()

# Singleton instance
event_publisher = EventPublisher()