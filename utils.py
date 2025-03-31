"""Utility functions for schedule validation, URL fetching, and rate limiting."""

import logging.config
import time

import asyncio
import httpx
import requests

import settings
from clients.notifications import EmailNotifier
from logging_config.logging_config import LOGGING_CONFIG
from settings import NOT_ALLOWED_CLASS_TYPE

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


semaphore = asyncio.Semaphore(settings.REQUESTS_PER_SECOND)


def fetch_url(url):
    """Fetch content from a URL with a 30-second timeout."""
    try:
        response = requests.get(url, timeout=30)
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""

    response.raise_for_status()
    return response.text


def check_valid_html(text):
    """Check if the HTML content is valid."""
    if hasattr(text, "text") and "error" in text.text.lower():
        return False
    return True


def check_valid_class_type(text):
    """Check if the class type is valid."""
    if text.lower() in NOT_ALLOWED_CLASS_TYPE:
        return False
    return True


def get_valid_instructor(text: str) -> (bool, str):
    """Get the valid instructor from the text."""
    for instructor in settings.INSTRUCTORS_WANTED:
        if instructor in text:
            return True, instructor
    return False, None


def get_valid_time(text: str) -> (bool, str, str):
    """Get the valid time from the text."""
    for time_wanted in settings.TIMES_WANTED:
        day = list(time_wanted.keys())[0]
        time_value = list(time_wanted.values())[0]
        if day in text and time_value in text:
            return True, day, time_value
    return False, None, None


def build_schedule(date_time_text, instructor, url):
    """Build the schedule."""
    data = {
        "date_time_text": date_time_text,
        "instructor": instructor,
        "url": url,
    }
    return data


async def trigger_schedule(class_id: int):
    """Trigger schedule for a specific class ID."""
    async with semaphore:
        start_time = time.monotonic()
        async with httpx.AsyncClient() as client:
            try:
                await client.post(f"{settings.BASE_URL}/schedule/{class_id}")
                logger.info("Successfully triggered schedule for class ID %s", class_id)
            except Exception as e:
                logger.error(
                    "Failed to trigger schedule for class ID %s: %s", class_id, e
                )
        # Calculate the time taken and adjust the rate
        elapsed = time.monotonic() - start_time
        wait_time = max(0, (1 / settings.REQUESTS_PER_SECOND) - elapsed)
        await asyncio.sleep(wait_time)


async def send_classes_report_email(body):
    """Send classes report email to pre-defined recipient emails."""
    breakpoint()
    await EmailNotifier().send_email(body=body)
