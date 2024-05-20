from playwright.sync_api import expect

from .utils import clean_full_url, retry


@retry()
def test_update_barrier(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    page.goto(clean_full_url(url))

    page.get_by_role("link", name="Add progress update").click()
    page.get_by_label("Barrier Progress").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_label("On Track Barrier will be").check()
    page.get_by_label("Explain why barrier resolution is on track").click()
    page.get_by_label("Explain why barrier resolution is on track").fill(
        "Test reasoning"
    )
    page.get_by_label("Month").click()
    page.get_by_label("Month").fill("05")
    page.get_by_label("Month").press("Tab")
    page.get_by_label("Year", exact=True).fill("2024")
    page.get_by_role("button", name="Save and continue").click()
    page.get_by_role("link", name="Confirm").click()

    expect(page.get_by_text("On track")).to_be_visible()
    expect(page.get_by_text("Test reasoning")).to_be_hidden()
