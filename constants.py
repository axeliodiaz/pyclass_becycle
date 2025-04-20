import os

ERROR_MESSAGE_INTEGER_REQUIRED = "Invalid class ID. It must be a positive integer."

# Redis
REDIS_KEY_SCHEDULES = "schedules"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_KEY = "schedules"
