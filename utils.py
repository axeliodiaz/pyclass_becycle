import requests

from settings import SCHEDULES_WANTED, NOT_ALLOWED_CLASS_TYPE


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


def get_valid_schedule(text, instructor=None):
    for schedule in SCHEDULES_WANTED:
        if (
            schedule["day"] in text
            and schedule["time"]
            and schedule["instructor"].lower() == instructor.lower()
        ):
            return True, schedule
    return False, {}


def show_schedule(schedule):
    schedule = {k: v for k, v in sorted(schedule.items(), key=lambda item: item[0])}
    print(
        f"{schedule['datetime'].format('dddd DD/MM (HH:mm)', locale='es').title()} [{schedule['instructor']}]: {schedule['url']}"
    )
