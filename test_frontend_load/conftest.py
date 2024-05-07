import os
import pytest
from playwright.async_api import sync_playwright

BASE_URL = os.getenv("BASE_FRONTEND_TESTING_URL", "http://market-access.local:9880/")
HEADLESS = os.getenv("TEST_HEADLESS", "false").lower() == "true"


@pytest.fixture(scope="session")
def session_data():
    """Return a dictionary to store session data."""
    return {
        "cookies": None,
        "barrier_id": None,
    }


@pytest.fixture(scope="session")
def playwright_instance():
    """Return a Playwright instance."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance):
    """Return a browser instance."""
    if HEADLESS:
        browser = playwright_instance.chromium.launch(headless=True)
    else:
        browser = playwright_instance.chromium.launch(slow_mo=100, headless=HEADLESS)
    yield browser
    browser.close()


@pytest.fixture(scope="session")
def context(browser, session_data):
    """Create a new browser context."""
    context = browser.new_context()
    context.set_default_timeout(0)

    # Initially, session_data["cookies"] will be None.
    # Check if "cookies" key exists and has a value; if not, it means it's the first test run.
    if session_data.get("cookies") is None:
        # Since it's the first run, let the browser context initiate and capture the cookies.
        session_data["cookies"] = context.cookies()
    else:
        # If it's not the first run, load the initially captured cookies into the context.
        context.add_cookies(session_data["cookies"])

    yield context
    context.close()


@pytest.fixture(scope="session")
def page(context):
    """Create a new page in the provided context."""
    _page = context.new_page()
    _page.goto(BASE_URL, wait_until="domcontentloaded")
    # Wait for the page to load
    _page.wait_for_timeout(10000)
    yield _page
