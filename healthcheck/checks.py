import requests
from django.conf import settings
from mohawk import Sender
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


def api_check():
    # TODO: figure why it works with metadata (200)
    #       but when calling check it comes back with (401)
    url = f"{settings.MARKET_ACCESS_API_URI}metadata"
    # url = f"{settings.MARKET_ACCESS_API_URI}check"
    sender = Sender(
        settings.MARKET_ACCESS_API_HAWK_CREDS,
        url,
        "GET",
        content="",
        content_type="text/plain",
        always_hash_content=False,
    )

    response = requests.get(
        url,
        verify=not settings.DEBUG,
        headers={"Authorization": sender.request_header, "Content-Type": "text/plain", },
    )

    # TODO: wrap up return, return data from API if 200, FAIL if anything else
    return True
