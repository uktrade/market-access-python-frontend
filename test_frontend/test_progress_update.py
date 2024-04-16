import pytest

from playwright.sync_api import expect

from .utils import clean_full_url, retry


@retry()
@pytest.mark.order(1)
def test_create_progress_update(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    page.goto(clean_full_url(url))

    page.get_by_role("link", name="Add progress update").click()
    page.get_by_label("Barrier progress").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_label("On Track Barrier will be").check()
    page.get_by_label("Explain why barrier resolution is on track").click()
    page.get_by_label("Explain why barrier resolution is on track").fill(
        "dsghidhfgjhoighdfihjg"
    )
    page.get_by_label("Month").click()
    page.get_by_label("Month").fill("10")
    page.get_by_label("Year", exact=True).click()
    page.get_by_label("Year", exact=True).fill("2024")
    page.get_by_role("button", name="Save and continue").click()
    page.locator("#next_step_item").click()
    page.locator("#next_step_item").fill("odhfgiuhdsoiuhdfg")
    page.locator("#next_step_owner").click()
    page.locator("#next_step_owner").fill("dhfgudhsug")
    page.get_by_label("Month").click()
    page.get_by_label("Month").fill("06")
    page.get_by_label("Year").click()
    page.get_by_label("Year").fill("2024")
    page.get_by_role("button", name="Save").click()

    link_locator = page.get_by_role("link", name="Confirm")
    link_locator.wait_for(state="visible", timeout=60000)  # Wait up to 60 seconds
    link_locator.click()

    expect(page.get_by_role("heading", name=title)).to_be_visible()
