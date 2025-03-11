import sys

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s - %(message)s",
            "use_colors": None,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        # Root logger to catch all logs
        "": {"handlers": ["default"], "level": "DEBUG"},
        # Uvicorn loggers
        "uvicorn": {"handlers": ["default"], "level": "DEBUG", "propagate": False},
        "uvicorn.error": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["default"],
            "level": "DEBUG",
            "propagate": False,
        },
        # Your app logger
        "__main__": {"handlers": ["default"], "level": "DEBUG", "propagate": False},
    },
}
