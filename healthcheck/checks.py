from sentry_sdk import capture_exception

from .constants import HealthStatus
from .models import HealthCheck


def db_check():
    """
    Performs a basic check on the database by performing a select query on a simple table
    :return: True or False according to successful retrieval
    """
    try:
        HealthCheck.objects.get(health_check_field=True)
        return HealthStatus.OK
    except Exception as e:
        capture_exception(e)
        return HealthStatus.FAIL
