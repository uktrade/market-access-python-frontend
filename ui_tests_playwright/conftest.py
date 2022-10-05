import os

import pytest

from ui_tests_playwright import settings as test_settings

os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


def pytest_configure(config):
    config.option.liveserver = test_settings.LIVE_SERVER_URL


@pytest.fixture(scope="function", autouse=True)
def sso_login_mock(settings):
    settings.SSO_AUTHORIZE_URI = test_settings.SSO_AUTHORIZE_URI
