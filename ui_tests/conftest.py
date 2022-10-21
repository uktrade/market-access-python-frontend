import json
import os

import pytest
from django.conf import settings

from barriers.models import HistoryItem
from core.filecache import memfiles
from ui_tests import settings as test_settings

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
