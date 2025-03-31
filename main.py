"""FastAPI application for managing class schedules with rate limiting and Redis storage."""

import asyncio
import logging.config
from urllib.parse import urljoin

import requests
from fastapi import FastAPI

import settings
from clients.redis import RedisClient
from constants import ERROR_MESSAGE_INTEGER_REQUIRED
from logging_config.logging_config import LOGGING_CONFIG
from single_version import create_schedules
from utils import trigger_schedule, send_classes_report_email

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
app = FastAPI()


@app.post("/")
async def root():
    """Trigger schedules for a range of class IDs using a semaphore rate limiter."""
    start_class_id = settings.SCHEDULE_ID_START
    limit = settings.SCHEDULES_LIMIT
    final_class_id = start_class_id + limit

    tasks = [
        asyncio.create_task(trigger_schedule(class_id))
        for class_id in range(start_class_id, final_class_id)
    ]

    # Wait for all tasks are completed
    await asyncio.gather(*tasks)

    if settings.SEND_EMAIL_REPORT:
        requests.post(urljoin(settings.BASE_URL, url="/schedules/send_email"))

    return {
        "message": f"Triggered schedules from class ID {start_class_id} to {final_class_id - 1}"
    }


@app.post("/schedule/{class_id}")
async def schedule_by_id(class_id: int):
    """Starts checking schedules from a specific class ID."""
    if class_id < 0:
        return {"error": ERROR_MESSAGE_INTEGER_REQUIRED}

    if not settings.ASYNC_MODE:
        _success, schedule = await create_schedules(class_id=class_id)
        return schedule

    asyncio.create_task(create_schedules(class_id=class_id))
    return {"message": f"Schedules for class ID {class_id} successfully triggered."}


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


@app.post("/schedules/send_email")
async def send_email_report_email():
    redis_client = RedisClient()
    schedules = await redis_client.get_all_schedules()
    body = ""
    logger.info("Sending email report.")
    requests.post(urljoin(settings.BASE_URL, url="/schedules/send_email"))
    for schedule in schedules:
        date_time_text = schedule["date_time_text"]
        instructor = schedule["instructor"]
        url = schedule["url"]
        body += f"{instructor}. {date_time_text}. <a href='{url}'>{url}</a>\n"

    await send_classes_report_email(body=body)
