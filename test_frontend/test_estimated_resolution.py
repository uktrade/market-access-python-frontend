import datetime

import pytest

from playwright.sync_api import expect

from .utils import clean_full_url, retry, generate_random_text


@retry()
@pytest.mark.order(2)
@pytest.mark.timeout(10)
def test_estimated_resolution_change_happy_path(page, create_test_barrier):
    title = "test"
    month = str(datetime.date.today().month + 1)
    year = str(datetime.date.today().year + 1)
    page.goto(clean_full_url(create_test_barrier(title=title)))
    page.get_by_role("link", name="Add estimated resolution date if applicable").click()
    page.get_by_label("Month").click()
    page.get_by_label("Month").fill("12")
    page.get_by_label("Year").click()
    page.get_by_label("Year").fill(year)
    page.locator("#reason").fill(generate_random_text())
    page.get_by_role("button", name="Save and return").click()

    page.locator(
        '#progress-update-link, a[href*="/progress_updates/barrier_progress"]'
    ).click()

    expect(
        page.get_by_role("heading", name="Add barrier progress update")
    ).to_be_visible()

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

    expect(page.get_by_text("You can now review the")).to_be_visible()

    page.get_by_role("link", name="Confirm").click()
