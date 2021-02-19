import pytest
from splinter import Browser

from ui_tests import settings
from ui_tests.helpers.auth import sso_sign_in


@pytest.fixture(scope="module")
def browser():
    browser = Browser(
        driver_name="remote", browser="chrome", command_executor=settings.WEB_DRIVER_URL
    )
    yield browser
    browser.quit()


@pytest.fixture(autouse=True)
def fixture_func(browser):
    if settings.TEST_SSO_LOGIN_URL:
        sso_sign_in(browser)
