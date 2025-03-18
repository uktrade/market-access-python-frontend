import datetime
import pytest
from playwright.sync_api import expect

from .utils import clean_full_url, retry, generate_random_text


@retry()
@pytest.mark.order(1)
def test_create_progress_update(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)

    month = str(datetime.date.today().month + 1)
    year = str(datetime.date.today().year + 1)

    page.goto(clean_full_url(url))

    page.get_by_role("link", name="Add progress update").click()
    page.get_by_label("Barrier progress").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_label("On Track", exact=True).check()
    page.get_by_label("Explain why barrier resolution is on track").fill(
        generate_random_text()
    )

    # Wait for save button to be enabled
    page.get_by_role("button", name="Save and continue").wait_for(state="visible")
    page.get_by_role("button", name="Save and continue").click()

    page.locator("#next_step_item").fill(generate_random_text())
    page.locator("#next_step_owner").fill(generate_random_text())
    page.get_by_label("Month").fill(month)
    page.get_by_label("Year").fill(year)
    page.get_by_role("button", name="Save").click()

    # Add wait time for confirmation message
    page.wait_for_timeout(1000)  # Wait for 1 second

    page.get_by_role("link", name="Confirm").click()
