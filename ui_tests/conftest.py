import pytest

from ui_tests import settings

from splinter import Browser


@pytest.fixture(scope="module")
def browser():
    browser = Browser(
        driver_name="remote",
        browser="chrome",
        command_executor=settings.WEB_DRIVER_URL,
    )
    yield browser
    browser.quit()
