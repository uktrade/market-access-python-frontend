import sys
from .base import *                 # noqa

from django_log_formatter_ecs import ECSFormatter


DJANGO_ENV = 'prod'

DEBUG = False

# Unable to put this in base.py because of circular import problem with ECSFormatter
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
