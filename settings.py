HOST = "localhost"
PORT = 8000
FULL_HOST = f"http://{HOST}:{PORT}"
SCHEDULE_URL = "https://becycle.cl/clase/{class_id}/"
INSTRUCTORS_WANTED = []
TIMES_WANTED = [
    {"Lunes": "07:15"},
    {"Martes": "07:15"},
    {"Miercoles": "07:15"},
    {"Miércoles": "07:15"},
    {"Jueves": "07:15"},
    {"Viernes": "07:15"},
    {"Sábado": "09:15"},
]

NOT_ALLOWED_CLASS_TYPE = ["beat"]
DEBUG = False

SCHEDULE_ID_START = 13469
SCHEDULES_LIMIT = 1000
REQUESTS_PER_SECOND = 10
ASYNC_MODE = True
