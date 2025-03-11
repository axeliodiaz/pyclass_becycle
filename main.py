import asyncio
import logging.config

import httpx
from fastapi import FastAPI

import settings
from logging_config import LOGGING_CONFIG
from single_version import get_schedules

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
app = FastAPI()


@app.get("/")
async def root():
    """Trigger both default and specific class ID via HTTP internally."""
    starting_class_id = settings.SCHEDULE_ID_START

    # Fire-and-forget HTTP request to trigger another schedule
    async def trigger_schedule():
        async with httpx.AsyncClient() as client:
            try:
                await client.get(f"{settings.FULL_HOST}/schedule/{starting_class_id}")
            except Exception as e:
                # Log the error instead of printing it
                logger.error(f"Failed to trigger schedule for class ID 150: {e}")

    # Schedule the HTTP request without waiting for it
    asyncio.create_task(trigger_schedule())

    message = f"Triggered schedules from default and specific class ID 150"
    return {"message": message}


@app.get("/schedule/{class_id}")
async def schedule_by_id(class_id: int):
    """Starts checking schedules from a specific class ID."""
    if class_id < 0:
        return {"error": "Invalid class ID. It must be a positive integer."}

    asyncio.create_task(get_schedules(class_id))
    message = f"Checked schedule class ID: {class_id}"
    return {"message": message}
