import sys

from django_log_formatter_ecs import ECSFormatter

from .base import *  # noqa
from .hardening import *  # noqa

DJANGO_ENV = "dev"

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
    "loggers": {"": {"handlers": ["ecs"], "level": DJANGO_LOG_LEVEL}},
}

# Dev environments have an extra user permission group to allow
# editing of user profiles without admin access
USER_ADDITIONAL_PERMISSION_GROUPS.append("Role administrator")
