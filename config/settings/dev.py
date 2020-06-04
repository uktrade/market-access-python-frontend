import sys
from .base import *                 # noqa

from django_log_formatter_ecs import ECSFormatter


DJANGO_ENV = 'dev'

DJANGO_LOG_LEVEL = env("DJANGO_LOG_LEVEL", default="info").upper()

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "ecs_formatter": {
            "()": ECSFormatter,
        },
    },
    "handlers": {
        "ecs": {
            "formatter": "ecs_formatter",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "": {
            "handlers": ["ecs"],
            "level": DJANGO_LOG_LEVEL
        }
    },
}
