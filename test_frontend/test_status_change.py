import datetime

import pytest
from playwright.sync_api import expect

from .utils import get_text_content_without_line_separators


@pytest.mark.order(1)
def test_change_status_unhappy_path(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    page.goto(url)

    page.get_by_role("link", name="Edit status").click()
    page.get_by_role("button", name="Save and return").click()

    assert page.locator(".govuk-error-summary__title").is_visible()
    assert (
        "Select the barrier status"
        in page.locator(".govuk-error-summary__list").text_content()
    )


@pytest.mark.order(2)
def test_status_change_happy_path(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    page.goto(url)

    assert page.url.endswith("/status/")
    page.get_by_label("Open").check()
    page.get_by_label(
        "Describe briefly the status of the barrier, including recent progress and any obstacles"
    ).click()
    page.get_by_label(
        "Describe briefly the status of the barrier, including recent progress and any obstacles"
    ).fill("test description")
    page.get_by_role("button", name="Save and return").click()

    assert (
        f"Barrier open on {datetime.datetime.now().strftime('%d %B %Y')}"
        in get_text_content_without_line_separators(
            page.locator(".barrier-status-details__heading").text_content()
        )
    )

    expect(page.locator(".barrier-status-details__text")).to_have_text(
        "test description"
    )

    # now let's change it to Resolved: In park
    page.get_by_role("link", name="Edit status").click()
    page.get_by_label("Resolved: In part").check()
    page.get_by_role("spinbutton", name="Day").click()
    page.get_by_role("spinbutton", name="Day").fill("01")
    page.get_by_role("spinbutton", name="Month").click()
    page.get_by_role("spinbutton", name="Month").fill("01")
    page.get_by_role("spinbutton", name="Year").click()
    page.get_by_role("spinbutton", name="Year").fill("2023")
    page.get_by_label(
        "Describe briefly how this barrier was partially resolved"
    ).click()
    page.get_by_label("Describe briefly how this barrier was partially resolved").fill(
        "description"
    )
    page.get_by_role("button", name="Save and return").click()

    assert (
        "Barrier partially resolved on 1 January 2023"
        in get_text_content_without_line_separators(
            page.locator(".barrier-status-details__heading").text_content()
        )
    )

    expect(page.locator(".barrier-status-details__text")).to_have_text("description")
