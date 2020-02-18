from .base import *     # noqa

DJANGO_ENV = 'local'
DEBUG = True

if not DEBUG:
    # offline compressing
    from .compress_offline import *     # noqa

# Remove VPN dependency
# metadata is pulled by the API from DataHub which is behind the VPN
MOCK_METADATA = True
