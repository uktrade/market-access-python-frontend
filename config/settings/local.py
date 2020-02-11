from .base import *  # noqa

DJANGO_ENV = 'local'

# Remove VPN dependency
# metadata is pulled by the API from DataHub which is behind the VPN
MOCK_METADATA = True
