import asyncio
import contextlib
import json
import logging
from typing import Any, Awaitable, Callable, Dict, Optional

import redis.asyncio as redis
from redis.asyncio.client import PubSub
from redis.asyncio.connection import ConnectionPool

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        self.redis_pool: Optional[ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
        self.pubsub: Optional[PubSub] = None
        self.callback: Optional[Callable[[str, Dict[str, Any]], Awaitable[None]]] = None
        self._reader_task: Optional[asyncio.Task] = None

    @property
    def is_connected(self) -> bool:
        return self.client is not None

    async def connect(self, host: str, port: int, db: int = 0, password: Optional[str] = None):
        try:
            self.redis_pool = ConnectionPool(
                host=host, port=port, db=db, password=password, decode_responses=True
            )
            self.client = redis.Redis(connection_pool=self.redis_pool)
            await self.client.ping()
            logger.info("Successfully connected to Redis at %s:%s", host, port)
        except Exception as e:
            logger.exception("Failed to connect to Redis: %s", e)
            self.client = None
            self.redis_pool = None
            raise

    async def disconnect(self):
        if self._reader_task:
            self._reader_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._reader_task
            self._reader_task = None

        if self.pubsub:
            await self.pubsub.close()
            self.pubsub = None

        if self.client:
            await self.client.aclose()
            self.client = None

        if self.redis_pool:
            self.redis_pool.disconnect(inuse_connections=True)
            self.redis_pool = None

        logger.info("Disconnected from Redis.")

    async def publish(self, room_name: str, message: Dict[str, Any]) -> int:
        if not self.client:
            logger.error("Cannot publish: Redis is not connected.")
            raise ConnectionError("Redis is not connected. Call connect() first.")

        channel = f"room:{room_name}"
        try:
            payload = json.dumps(message)
            subscribers = await self.client.publish(channel, payload)
            logger.debug("Published message to '%s' (subscribers: %d)", channel, subscribers)
            return subscribers
        except Exception:
            logger.exception("Failed to publish to %s", channel)
            raise

    async def subscribe(self, room_name: str):
        if not self.pubsub:
            raise ConnectionError("Subscriber not started. Call start_subscriber() first.")
        await self.pubsub.subscribe(f"room:{room_name}")
        logger.info("Subscribed to Redis channel 'room:%s'", room_name)

    async def start_subscriber(self, callback: Callable[[str, Dict[str, Any]], Awaitable[None]]):
        if not self.client:
            raise ConnectionError("Redis is not connected. Call connect() first.")

        self.callback = callback
        self.pubsub = self.client.pubsub()
        await self.pubsub.psubscribe("room:*")  # no trailing space

        self._reader_task = asyncio.create_task(self._reader())

    async def _reader(self):
        assert self.pubsub is not None
        logger.info("Redis listener task started.")
        try:
            while True:
                msg = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if not msg:
                    await asyncio.sleep(0.01)  # avoid busy loop
                    continue

                channel = msg.get("channel")
                data_str = msg.get("data")
                if not isinstance(channel, str) or not channel.startswith("room:") or data_str is None:
                    continue

                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    logger.warning("Discarding non-JSON payload on %s: %r", channel, data_str)
                    continue

                if self.callback:
                    room_name = channel.split(":", 1)[1]
                    await self.callback(room_name, data)

        except asyncio.CancelledError:
            pass
        except Exception:
            logger.exception("Error in Redis listener loop")
            await asyncio.sleep(1.0)

redis_manager = RedisManager()