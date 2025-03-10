from bs4 import BeautifulSoup
import arrow

import settings
from utils import (
    check_valid_html,
    check_valid_class_type,
    get_valid_schedule,
    check_valid_instructor,
    fetch_url,
    show_schedule,
)


def get_schedules():
    found_schedules = 0
    errors = 0
    schedules = []

    for class_id in range(settings.SCHEDULE_ID_START, settings.SCHEDULE_ID_FINISH):
        # while class_id < settings.SCHEDULE_ID_FINISH:
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
            errors += 1
            class_id += 1
            if settings.DEBUG:
                print(f"Passing by error ID {class_id}. Error {errors}")

            """
            if errors >= settings.MAX_CONSECUTIVE_ERRORS:
                print(
                    f"Finishing execution due to {settings.MAX_CONSECUTIVE_ERRORS} consecutive errors. Last ID: {class_id}"
                )
                break
            """
            continue

        schedule["url"] = url

        # show_schedule(schedule)
        schedules.append(schedule)
        class_id += 1
        found_schedules += 1

    return schedules


def parse_schedule(html):
    soup = BeautifulSoup(html, features="html.parser")
    main_text = soup.find("main")

    if not check_valid_html(main_text):
        return {"error": "error"}

    date_time_text = soup.find("div", class_="fecha").text
    title_text = soup.find("div", class_="name").text

    day = date_time_text.split()[1]

    instructor = title_text.split()[-1]

    year = "2025"
    month_MMMM = date_time_text.split()[3].replace(",", "")

    _time = date_time_text.split()[-2].split(":")
    _hour = _time[0]
    _minutes = _time[1]
    date_time = arrow.get(
        f"{year}/{month_MMMM}/{day} {_hour}:{_minutes}",
        "YYYY/MMMM/DD HH:mm",
        locale="es",
    )

    if arrow.utcnow() > date_time or month_MMMM == "Diciembre":
        return {}

    schedule = {"datetime": date_time, "instructor": instructor}

    if date_time.format("dddd", locale="es").title() in [
        "Miercoles",
        "Miércoles",
        "Lunes",
        "Viernes",
    ]:
        if date_time.format("HH:mm") == "07:15":
            if instructor in settings.WANTED_INSTRUCTORS:
                show_schedule(schedule)
                return schedule

    if (
        date_time.format("dddd", locale="es").title() in ["Sabado", "Sábado"]
        and date_time.format("HH:mm") == "09:15"
        and instructor in settings.WANTED_INSTRUCTORS
    ):
        return schedule

    return {}


if __name__ == "__main__":
    schedules = get_schedules()
    schedules = sorted(schedules, key=lambda x: x["datetime"])
    for schedule in schedules:
        show_schedule(schedule)
