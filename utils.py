import logging.config

import httpx
import requests

import settings
from logging_config.logging_config import LOGGING_CONFIG
from settings import SCHEDULES_WANTED, NOT_ALLOWED_CLASS_TYPE

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def fetch_url(url):
    try:
        response = requests.get(url)
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""

    response.raise_for_status()
    return response.text


def check_valid_html(text):
    if hasattr(text, "text") and "error" in text.text.lower():
        return False
    return True


def check_valid_class_type(text):
    if text.lower() in NOT_ALLOWED_CLASS_TYPE:
        return False
    return True


def check_valid_instructor(schedule, text):
    return schedule["instructor"] in text


def get_valid_schedule(text):
    for schedule in SCHEDULES_WANTED:
        if schedule["day"] in text and schedule["time"] in text:
            return True, schedule
    return False, {}


async def trigger_schedule(class_id: int):
    """Trigger schedule for a specific class ID."""
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{settings.FULL_HOST}/schedule/{class_id}")
            logger.info(f"Successfully triggered schedule for class ID {class_id}")
        except Exception as e:
            logger.error(f"Failed to trigger schedule for class ID {class_id}: {e}")
