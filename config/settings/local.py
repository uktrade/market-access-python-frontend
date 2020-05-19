from .base import *     # noqa

from django.utils.log import DEFAULT_LOGGING

DJANGO_ENV = 'local'
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
DEBUG = True

if not DEBUG:
    # offline compressing
    from .compress_offline import *     # noqa

# Remove VPN dependency
# metadata is pulled by the API from DataHub which is behind the VPN
MOCK_METADATA = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            # exact format is not important, this is the minimum information
            'format': '[%(asctime)s] %(name)s %(levelname)5s - %(message)s',
        },
        'django.server': DEFAULT_LOGGING['formatters']['django.server'],
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'django.server': DEFAULT_LOGGING['handlers']['django.server'],
    },
    'loggers': {
        # root logger
        '': {
            'level': 'WARNING',
            'handlers': ['console'],
        },
        'market-access-python-frontend': {
            'level': DJANGO_LOG_LEVEL,      # noqa
            'handlers': ['console'],
            # required to avoid double logging with root logger
            'propagate': False,
        },
        'django.server': DEFAULT_LOGGING['loggers']['django.server'],
    },
}
