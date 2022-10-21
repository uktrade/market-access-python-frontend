import json
import os

import pytest
from django.conf import settings

from barriers.models import HistoryItem
from core.filecache import memfiles
from ui_tests import settings as test_settings
from utils.api.client import MarketAccessAPIClient

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


def pytest_configure(config):
    config.option.liveserver = test_settings.LIVE_SERVER_URL


@pytest.fixture(scope="function", autouse=True)
def sso_login_mock(settings):
    settings.SSO_AUTHORIZE_URI = test_settings.SSO_AUTHORIZE_URI


@pytest.fixture(autouse=True)
def always_run_live_server(live_server):
    pass


@pytest.fixture()
def barrier_history():
    file = f"{settings.BASE_DIR}/../tests/barriers/fixtures/history.json"
    history_data = json.loads(memfiles.open(file))
    history = [HistoryItem(result) for result in history_data[0]]
    return history


@pytest.fixture()
def test_barrier_id():
    # Many tests need a valid barrier id to call the correct URL
    # Non-permanent solution; get an existing barrier in the db and use
    # that ID. You will need to have created a barrier locally for the
    # tests to work. Patch any further API calls to simulate the data you
    # want the API to return.
    client = MarketAccessAPIClient()
    barrier_list = client.barriers.list()
    barrier_id = barrier_list[0]["id"]
    return barrier_id
