"""Base settings for the application."""

HOST = "localhost"
PORT = 8000
BASE_URL = f"http://{HOST}:{PORT}"
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
    {"Sabado": "09:15"},
]

NOT_ALLOWED_CLASS_TYPE = ["beat"]
DEBUG = False

SCHEDULE_ID_START = 14000
SCHEDULES_LIMIT = 500
REQUESTS_PER_SECOND = 10
ASYNC_MODE = True

# Email settings (to be overridden in local.py)
EMAIL_SENDER = None
EMAIL_PASSWORD = None
EMAIL_RECIPIENTS = []
SEND_EMAIL_REPORT = False
EMAIL_SUBJECT = "New classes schedules"

# Mailtrap API settings (used when DEBUG=True)
MAILTRAP_API_TOKEN = ""
MAILTRAP_API_HOST = "sandbox.api.mailtrap.io"
MAILTRAP_INBOX_ID = ""  # Your inbox ID

# SendGrid settings (used when DEBUG=False)
SENDGRID_API_VERSION = "v3"

NEXT_WEEKS_NOTIFICATION = 0
