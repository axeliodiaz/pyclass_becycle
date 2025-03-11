import json
import logging

import redis.asyncio as redis

from constants import REDIS_PORT, REDIS_HOST, REDIS_KEY

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self):
        self._redis = None

    async def _connect(self):
        """Establish the connection to Redis if not already connected."""
        if self._redis is None:
            self._redis = redis.Redis(
                host=REDIS_HOST, port=REDIS_PORT, decode_responses=True
            )
            try:
                await self._redis.ping()
                logger.info("Connected to Redis automatically.")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                self._redis = None

    async def _get_client(self):
        """Ensure Redis client is connected."""
        if self._redis is None:
            await self._connect()
        return self._redis

    async def save_schedule(self, schedule: dict):
        """Save a schedule in Redis."""
        redis_conn = await self._get_client()
        if not redis_conn:
            logger.error("Redis connection is not established.")
            return

        try:
            await redis_conn.rpush(REDIS_KEY, json.dumps(schedule))
        except Exception as e:
            logger.error(f"Error saving schedule to Redis: {e}")
        else:
            logger.debug(f"Saved schedule to Redis: {schedule}")
            logger.info(
                f"{schedule['day']} ({schedule['time']}). {schedule['url']} con {schedule['instructor']}\n"
            )

    async def get_all_schedules(self):
        """Retrieve all schedules from Redis."""
        redis_conn = await self._get_client()
        logger.debug("Redis connection is not established.")

        if not redis_conn:
            logger.error("Redis connection is not established.")
            return []

        try:
            schedules = await redis_conn.lrange(REDIS_KEY, 0, -1)
            logger.info(f"Retrieved {len(schedules)} schedules from Redis: {schedules}")
        except Exception as e:
            logger.error(f"Error retrieving schedules from Redis: {e}")
            return []

        return [json.loads(schedule) for schedule in schedules]

    async def disconnect(self):
        """Close the Redis connection."""
        if self._redis:
            await self._redis.close()
            logger.info("Redis connection closed.")
            self._redis = None

    async def clear_schedules(self):
        """Delete only the schedules list from Redis."""
        redis_conn = await self._get_client()
        try:
            await redis_conn.delete(REDIS_KEY)
            logger.info("Schedules list cleared from Redis successfully.")
        except Exception as e:
            logger.error(f"Failed to clear schedules list from Redis: {e}")
