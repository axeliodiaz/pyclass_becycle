import asyncio
import logging.config

from fastapi import FastAPI
import httpx
import time

import settings
from clients.redis import RedisClient
from constants import ERROR_MESSAGE_INTEGER_REQUIRED
from logging_config.logging_config import LOGGING_CONFIG
from single_version import get_schedules
from utils import trigger_schedule

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
app = FastAPI()


@app.get("/")
async def root():
    """Trigger schedules for a range of class IDs using a semaphore rate limiter."""
    start_class_id = settings.SCHEDULE_ID_START
    limit = settings.SCHEDULES_LIMIT
    final_class_id = start_class_id + limit

    semaphore = asyncio.Semaphore(settings.REQUESTS_PER_SECOND)

    async def trigger_schedule(class_id: int):
        """Trigger schedule for a specific class ID."""
        async with semaphore:
            start_time = time.monotonic()
            async with httpx.AsyncClient() as client:
                try:
                    await client.post(f"{settings.FULL_HOST}/schedule/{class_id}")
                    logger.info(
                        f"Successfully triggered schedule for class ID {class_id}"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to trigger schedule for class ID {class_id}: {e}"
                    )
            # Calculate the time taken and adjust the rate
            elapsed = time.monotonic() - start_time
            wait_time = max(0, (1 / settings.REQUESTS_PER_SECOND) - elapsed)
            await asyncio.sleep(wait_time)

    tasks = [
        asyncio.create_task(trigger_schedule(class_id))
        for class_id in range(start_class_id, final_class_id)
    ]

    # Esperar a que todas las tareas se completen
    await asyncio.gather(*tasks)

    return {
        "message": f"Triggered schedules from class ID {start_class_id} to {final_class_id - 1}"
    }


@app.post("/schedule/{class_id}")
async def schedule_by_id(class_id: int):
    """Starts checking schedules from a specific class ID."""
    if class_id < 0:
        return {"error": ERROR_MESSAGE_INTEGER_REQUIRED}

    asyncio.create_task(get_schedules(class_id))
    message = f"Checked schedule class ID: {class_id}"
    return {"message": message}


@app.get("/schedules")
async def read_schedules():
    """Retrieve all schedules."""
    logger.warning("Retrieving schedules from Redis")
    redis_client = RedisClient()
    schedules = await redis_client.get_all_schedules()
    return {"schedules": schedules}


@app.delete("/schedules/clear")
async def clear_schedules():
    """Clear only the schedules list from Redis."""
    redis_client = RedisClient()
    await redis_client.clear_schedules()
    return {"message": "Schedules list cleared."}
