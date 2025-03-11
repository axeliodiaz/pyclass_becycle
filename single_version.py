import logging.config

import aiohttp
from bs4 import BeautifulSoup

import settings
from logging_config.logging_config import LOGGING_CONFIG
from utils import (
    check_valid_html,
    check_valid_class_type,
    get_valid_schedule,
    check_valid_instructor,
    save_schedule,
)

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


async def fetch_url(session, url):
    """Asynchronously fetches the content of a URL."""
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


async def parse_schedule(html):
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

    is_schedule_valid, schedule = get_valid_schedule(text=date_time_text)
    if not is_schedule_valid:
        return {"error": "is_schedule_valid"}

    if not check_valid_instructor(schedule, title_text):
        return {"error": "check_valid_instructor"}

    # Extract the day from the date_time text
    schedule["day"] = date_time_text.split(",")[0]
    return schedule


async def process_schedule(session, class_id):
    """Processes a specific schedule by its class ID."""
    url = settings.SCHEDULE_URL.format(class_id=class_id)
    html = await fetch_url(session, url)
    schedule = await parse_schedule(html)
    if schedule and "error" not in schedule:
        schedule["url"] = url
        save_schedule(schedule)
        return True, 0
    else:
        return False, 1


async def get_schedules(class_id: int):
    """Main function to retrieve schedules starting from a given class ID."""
    async with aiohttp.ClientSession() as session:
        success, error = await process_schedule(session, class_id)
        if not success:
            logger.warning(f"Error at ID {class_id}. Success: {success}")
