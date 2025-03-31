"""Module for fetching and parsing class schedules from a single URL."""

import logging.config

import aiohttp
from bs4 import BeautifulSoup

import settings
from clients.redis import RedisClient
from logging_config.logging_config import LOGGING_CONFIG
from utils import (
    check_valid_html,
    check_valid_class_type,
    get_valid_time,
    build_schedule,
    get_valid_instructor,
)

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


async def fetch_url(session, url):
    """Asynchronously fetches the content of a URL."""
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except aiohttp.ClientError as e:
        logger.error("Error fetching %s: %s", url, e)
        return None


async def parse_schedule(html, url):
    """Parses the HTML content to extract the schedule."""
    if not html:
        return {"error": "error"}

    soup = BeautifulSoup(html, features="html.parser")
    main_text = soup.find("main")

    if not check_valid_html(main_text):
        return {"error": "check_valid_html"}

    date_time = soup.find("div", class_="fecha")
    title = soup.find("div", class_="name")

    if not date_time or not title:
        return {"error": "date_time or title"}

    date_time_text = date_time.text
    title_text = title.text

    if not check_valid_class_type(text=title_text):
        return {"error": "check_valid_class_type"}

    is_valid_time, _, _ = get_valid_time(text=date_time_text)
    if not is_valid_time:
        return {"error": "get_valid_time"}

    is_valid_instructor, instructor = get_valid_instructor(text=title_text)
    if not is_valid_instructor:
        return {"error": "check_valid_instructor"}

    schedule = build_schedule(
        date_time_text=date_time_text,
        instructor=instructor,
        url=url,
    )
    return schedule


async def process_schedule(session, class_id):
    """Processes a specific schedule by its class ID.

    data = {
        "date_time_text": date_time_text,
        "instructor": instructor,
        "url": url,
    }
    """
    url = settings.SCHEDULE_URL.format(class_id=class_id)
    html = await fetch_url(session, url)
    schedule = await parse_schedule(html, url)
    redis_client = RedisClient()
    if schedule and "error" not in schedule:
        schedule["url"] = url
        await redis_client.save_schedule(schedule)
        return True, schedule
    else:
        logger.error(schedule)
        return False, schedule


async def create_schedules(class_id: int):
    """Main function to retrieve schedules starting from a given class ID."""
    async with aiohttp.ClientSession() as session:
        success, schedule = await process_schedule(session, class_id)
        if not success:
            logger.warning(
                "Error at ID %s. Success: %s. %s", class_id, success, schedule
            )
        return success, schedule
