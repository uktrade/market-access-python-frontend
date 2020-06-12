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
    data = {
        "status": HealthStatus.FAIL,
        "respose_time": None
    }
    # trailing / is important here
    url = f"{settings.MARKET_ACCESS_API_URI}check/"
    sender = Sender(
        settings.MARKET_ACCESS_API_HAWK_CREDS,
        url,
        "GET",
        content="",
        content_type="text/plain",
        always_hash_content=False,
    )

    try:
        response = requests.get(
            url,
            verify=not settings.DEBUG,
            headers={"Authorization": sender.request_header, "Content-Type": "text/plain", },
        )
        response.raise_for_status()
        response_data = response.json()
    except Exception:
        pass
    else:
        data["status"] = response_data["status"]
        data["duration"] = response_data.get("duration")

    return data
