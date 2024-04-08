import pytest
from playwright.sync_api import expect

from .utils import clean_full_url


@pytest.mark.order(1)
def test_report_a_barrier_page(page):
    page.get_by_role("button", name="Report a barrier Add a market").click()
    expect(
        page.get_by_role("heading", name="Market access barriers Report")
    ).to_be_visible()


@pytest.mark.order(2)
def test_change_barrier_priority(page, create_test_barrier):

    title = "test"
    url = create_test_barrier(title=title)
    page.goto(clean_full_url(url))

    page.get_by_role("link", name="Activate link to change").click()
    page.locator("#confirm-priority-yes").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_label(
        "Top 100 priority barrier Barrier needs significant input from DBT policy teams"
    ).check()
    page.get_by_label("Describe why this should be").click()
    page.get_by_label("Describe why this should be").fill(
        "this is a top 100 priority barrier"
    )
    page.get_by_role("button", name="Save and return").click()

    expect(page.get_by_role("heading", name=title)).to_be_visible()


@pytest.mark.order(3)
def test_change_top_100_status(page, create_test_barrier):

    title = "test"
    url = create_test_barrier(title=title)
    page.goto(clean_full_url(url))

    # add tag top 100 priority
    page.get_by_role("link", name="Edit tags").click()
    page.get_by_label("Programme Fund").check()
    page.get_by_label("Scoping (Top 100 priority").check()
    page.get_by_role("button", name="Save changes").click()

    # change status to top 100 priority
    page.get_by_role("link", name="Add progress update").click()
    page.get_by_label("Barrier progress").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_label("On Track Barrier will be").check()
    page.get_by_label("Explain why barrier resolution is on track").click()
    page.get_by_label("Explain why barrier resolution is on track").fill(
        "because it is being resolved"
    )
    page.get_by_label("Month").click()
    page.get_by_label("Month").fill("10")
    page.get_by_label("Year", exact=True).click()
    page.get_by_label("Year", exact=True).fill("2024")
    page.get_by_role("button", name="Save and continue").click()
    page.locator("#next_step_item").click()
    page.locator("#next_step_item").fill("check documents")
    page.locator("#next_step_owner").click()
    page.locator("#next_step_owner").fill("the next investigator")
    page.get_by_label("Month").click()
    page.get_by_label("Month").fill("8")
    page.get_by_label("Year").click()
    page.get_by_label("Year").fill("2024")
    page.get_by_role("button", name="Save").click()
    page.get_by_role("link", name="Confirm").click()

    expect(page.get_by_text("On track")).to_be_visible()


@pytest.mark.order(4)
def test_add_tag(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    page.goto(clean_full_url(url))

    page.get_by_role("link", name="Edit tags").click()
    page.get_by_label("Programme Fund").check()
    page.get_by_label("Scoping (Top 100 priority").check()
    page.get_by_role("button", name="Save changes").click()


@pytest.mark.order(5)
def test_update_sector(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    page.goto(clean_full_url(url), wait_until="load")

    page.get_by_label("edit main sector").click()
    page.get_by_role("combobox").select_option("9b38cecc-5f95-e211-a939-e4115bead28a")
    page.get_by_role("button", name="Add main sector").click()
    page.get_by_text("Chemicals").click()
    expect(page.get_by_text("Chemicals")).to_be_visible()
