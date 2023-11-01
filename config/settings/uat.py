import sys

from django_log_formatter_ecs import ECSFormatter

from .base import *  # noqa

DJANGO_ENV = "uat"

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

# The following are extra-permission groups (not roles)
# Adding a user to these groups should not remove the role from the user
# UAT environments have an extra user permission group to allow
# editing of user profiles without admin access
USER_ADDITIONAL_PERMISSION_GROUPS = [
    "Download approved user",
    "Action plan user",
    "PB100 barrier approver",
    "Role administrator",
]
