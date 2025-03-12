import logging.config

import httpx
import requests

import settings
from logging_config.logging_config import LOGGING_CONFIG
from settings import NOT_ALLOWED_CLASS_TYPE

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


def get_valid_instructor(text: str) -> (bool, str):
    for instructor in settings.INSTRUCTORS_WANTED:
        if instructor in text:
            return True, instructor
    return False, None


def get_valid_time(text: str) -> (bool, str, str):
    for time_wanted in settings.TIMES_WANTED:
        day = list(time_wanted.keys())[0]
        time = list(time_wanted.values())[0]
        if day in text and time in text:
            return True, day, time
    return False, None, None


def build_schedule(date_time_text, instructor, url):
    data = {
        "date_time_text": date_time_text,
        "instructor": instructor,
        "url": url,
    }
    return data


async def trigger_schedule(class_id: int):
    """Trigger schedule for a specific class ID."""
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{settings.FULL_HOST}/schedule/{class_id}")
            logger.info(f"Successfully triggered schedule for class ID {class_id}")
        except Exception as e:
            logger.error(f"Failed to trigger schedule for class ID {class_id}: {e}")
