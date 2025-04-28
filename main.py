"""FastAPI application for managing class schedules with rate limiting and Redis storage."""

import asyncio
import logging.config
import os
from urllib.parse import urljoin

import arrow
import requests
from fastapi import FastAPI

import settings
from clients.redis import RedisClient
from constants import ERROR_MESSAGE_INTEGER_REQUIRED
from logging_config.logging_config import LOGGING_CONFIG
from single_version import create_schedules
from utils import trigger_schedule, send_classes_report_email, get_next_week_schedules

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
app = FastAPI()


@app.post("/")
async def root():
    """Trigger schedules for a range of class IDs without waiting for tasks to complete."""
    start_class_id = settings.SCHEDULE_ID_START
    limit = settings.SCHEDULES_LIMIT
    final_class_id = start_class_id + limit

    for class_id in range(start_class_id, final_class_id):
        asyncio.create_task(trigger_schedule(class_id))

    if settings.SEND_EMAIL_REPORT:
        requests.post(urljoin(settings.BASE_URL, url="/schedules/send_email"))

    return {
        "message": f"Triggered schedules from class ID {start_class_id} to {final_class_id - 1} (async started)"
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
    schedules_sorted = sorted(schedules, key=lambda s: arrow.get(s["datetime"]))

    # Get filtered schedules and date range
    filtered_schedules, date_range = get_next_week_schedules(schedules=schedules_sorted)
    start_date, end_date = date_range

    # Format dates in a user-friendly way (e.g., "Monday, May 6" to "Sunday, May 12")
    start_date_formatted = start_date.format('dddd, MMMM D', locale='en')
    end_date_formatted = end_date.shift(days=-1).format('dddd, MMMM D', locale='en')  # End date is exclusive, so subtract 1 day
    date_range_text = f"{start_date_formatted} to {end_date_formatted}"

    # Read the HTML template file
    template_path = os.path.join('templates', 'emails', 'class_schedule.html')
    with open(template_path, 'r') as template_file:
        template = template_file.read()

    # Generate the class items HTML
    class_items_html = ""
    for schedule in filtered_schedules:
        date_time_text = schedule["date_time_text"]
        instructor = schedule["instructor"]
        url = schedule["url"]
        location = schedule.get("location", "")
        location_html = f'<div class="location">{location}</div>' if location else ""
        class_items_html += f"""
        <div class="class-item">
            <div class="instructor">{instructor}</div>
            <div class="date-time">{date_time_text}</div>
            {location_html}
            <a href="{url}" class="class-link">Book this class</a>
        </div>
        """

    # Add date range information to the template
    date_range_html = f"""
    <div class="alert alert-info" role="alert">
        <p>Schedule for: <strong>{date_range_text}</strong></p>
    </div>
    """

    # Replace the placeholder with the generated class items HTML and add date range
    body = template.replace('{class_items}', date_range_html + class_items_html)

    await send_classes_report_email(body=body)
    return {"message": "Email sending."}
