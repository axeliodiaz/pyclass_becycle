from bs4 import BeautifulSoup

import settings
from utils import check_valid_html, check_valid_class_type, get_valid_schedule, check_valid_instructor, fetch_url, \
    show_schedule


def get_schedules():
    should_check = True
    found_schedules = 0
    class_id = settings.SCHEDULE_ID_START

    while should_check:
        url = settings.SCHEDULE_URL.format(class_id=class_id)

        html = fetch_url(url)
        schedule = parse_schedule(html)

        if not schedule:
            if settings.DEBUG:
                print(f"Not found schedule in class ID {class_id}")
            class_id += 1
            continue

        if "error" in schedule.keys():
            if settings.DEBUG:
                print(f"Error in class ID {class_id}")
            break

        schedule["url"] = url
        show_schedule(schedule)
        class_id += 1
        found_schedules += 1
        if found_schedules >= 10:
            break


def parse_schedule(html):
    soup = BeautifulSoup(html, features="html.parser")
    schedules = []
    main_text = soup.find("main")

    if not check_valid_html(main_text):
        return {"error": "error"}

    date_time_text = soup.find("div", class_="fecha").text
    title_text = soup.find("div", class_="name").text

    if not check_valid_class_type(text=title_text):
        return schedules

    is_schedule_valid, schedule = get_valid_schedule(text=date_time_text)
    if not is_schedule_valid:
        return schedules

    if not check_valid_instructor(schedule, title_text):
        return schedules

    schedule["day"] = date_time_text.split(",")[0]
    return schedule


if __name__ == "__main__":
    get_schedules()