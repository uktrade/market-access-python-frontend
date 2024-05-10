import datetime
import os
import random
import string

import pytest
from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("BASE_FRONTEND_TESTING_URL", "http://market-access.local:9880/")
HEADLESS = os.getenv("TEST_HEADLESS", "false").lower() == "true"


@pytest.fixture(scope="session")
def session_data():
    """Return a dictionary to store session data."""
    return {
        "cookies": None,
        "barrier_id": None,
        "barrier_title": "",
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
    # Create a new browser context
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
    # Create a new page in the provided context
    _page = context.new_page()
    _page.goto(BASE_URL, wait_until="domcontentloaded")
    # Wait for the page to load
    _page.wait_for_timeout(10000)
    yield _page


@pytest.fixture(scope="session")
def create_test_barrier(page, session_data):
    def _create_test_barrier(title):

        if session_data["barrier_id"]:
            return f'{BASE_URL}barriers/{session_data["barrier_id"]}/'

        random_barrier_id = "".join(
            random.choice(string.ascii_uppercase) for _ in range(5)
        )
        random_barrier_name = f"{title} - {datetime.datetime.now().strftime('%d-%m-%Y')} - {random_barrier_id}"

        session_data["barrier_title"] = random_barrier_name

        page.get_by_role("link", name="Report a barrier").click()
        page.get_by_role("link", name="Start now").click()
        page.get_by_label("Barrier title").click()
        page.get_by_label("Barrier title").fill(random_barrier_name)
        page.get_by_label("Barrier description").click()
        page.get_by_label("Barrier description").fill("test description")
        page.get_by_role("button", name="Continue").click()

        page.locator("#status-radio-2").check()
        page.locator("#status-radio-3").check()
        page.locator(
            "#status-date-group-barrier-status-partially_resolved_date_0"
        ).click()
        page.locator(
            "#status-date-group-barrier-status-partially_resolved_date_0"
        ).fill("04")
        page.locator(
            "#status-date-group-barrier-status-partially_resolved_date_1"
        ).click()
        page.locator(
            "#status-date-group-barrier-status-partially_resolved_date_1"
        ).fill("2023")
        page.locator("#id_barrier-status-partially_resolved_description").click()
        page.locator("#id_barrier-status-partially_resolved_description").fill(
            "ifdshgihsdpihgf"
        )
        page.locator("#status-date-group-barrier-status-start_date_0").click()
        page.locator("#status-date-group-barrier-status-start_date_0").fill("03")
        page.locator("#status-date-group-barrier-status-start_date_1").click()
        page.locator("#status-date-group-barrier-status-start_date_1").fill("2024")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("combobox").select_option("TB00016")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("radio").first.check()
        page.get_by_role("button", name="Continue").click()
        page.locator("#main_sector_select").select_option(
            "9538cecc-5f95-e211-a939-e4115bead28a"
        )
        page.get_by_text("Add sector").click()
        page.locator("#sectors_select").select_option(
            "9738cecc-5f95-e211-a939-e4115bead28a"
        )
        page.get_by_text("Other sectors (optional) Add").click()
        page.locator("#sectors_select").select_option(
            "9638cecc-5f95-e211-a939-e4115bead28a"
        )
        page.get_by_role("button", name="Continue").click()
        page.get_by_placeholder("Search Company").click()
        page.locator("#search-companies-button").click()
        page.get_by_placeholder("Search Company").fill("Test LTD")
        page.get_by_placeholder("Search Company").press("Enter")
        page.get_by_text("TEST LIMITEDCompanies House").click()
        page.get_by_text("Add company").click()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Goods", exact=True).check()
        page.get_by_label("Services", exact=True).check()
        page.get_by_label("Which goods, services or").click()
        page.get_by_label("Which goods, services or").fill("isfdgihisdhfgidsfg")
        page.get_by_role("button", name="Continue").click()

        # MAU extra fields
        page.get_by_label("Yes, it can be published once").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Now").check()
        page.get_by_role("button", name="Continue").click()
        page.locator("#id_barrier-public-title-title").fill("Test barrier public")
        page.locator("summary").click()
        page.get_by_role("button", name="Continue").click()
        page.locator("#id_barrier-public-summary-summary").fill("public summary")
        page.get_by_role("button", name="Continue").click()

        # saveand return to barrier page
        page.get_by_role("button", name="Continue").click()

        page.wait_for_timeout(5)

        session_data["barrier_id"] = page.url.split("/")[-3]
        return f'{BASE_URL}/barriers/{session_data["barrier_id"]}/'

    return _create_test_barrier
