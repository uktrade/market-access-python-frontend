import logging

import pytest
from playwright.sync_api import expect

from test_frontend.utils import (
    change_permissions,
    clean_full_url,
    get_base_url,
    get_username,
    retry,
)

LOGGER = logging.getLogger(__name__)


@retry()
def test_successful_publish(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    barrier_details_url = clean_full_url(url)

    page.goto(barrier_details_url + "public")
    page.get_by_role("button", name="Submit for review").click()
    page.get_by_role("heading", name="This barrier is now awaiting").click()

    expect(page.get_by_text("This barrier is now awaiting approval")).to_be_visible()

    change_permissions(
        page,
        get_username(page),
        "Public barrier approver",
    )
    page.goto(barrier_details_url + "public")
    page.get_by_role("link", name="Review barrier").click()
    page.locator('input[name="content_clearance"]').check()
    page.locator('input[name="external_clearances"]').check()
    page.get_by_role("button", name="Send to GOV.UK content team").click()

    expect(
        page.get_by_text(
            "This barrier has been approved and is now with the GOV.UK content team"
        )
    ).to_be_visible()

    change_permissions(
        page,
        get_username(page),
        "Publisher",
    )
    page.goto(barrier_details_url + "public")
    page.get_by_role("link", name="Publish", exact=True).click()

    expect(
        page.get_by_text("Confirm you want to publish this barrier on GOV.UK")
    ).to_be_visible()

    # Barriers cannot be published on your local environment
    if get_base_url() != "http://market-access.local:9880/":
        page.get_by_role("button", name="Confirm").click()

        expect(
            page.get_by_text("This barrier has been published on GOV.UK")
        ).to_be_visible()


@pytest.mark.skipif(
    get_base_url() == "http://market-access.local:9880/",
    reason="Barriers cannot be published on your local environment",
)
def test_unpublish(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)

    page.goto(clean_full_url(url) + "public")
    page.get_by_role("link", name="Unpublish").click()
    page.locator("#id_public_publisher_summary").fill("Test")
    page.get_by_role("button", name="Confirm").click()

    expect(page.get_by_text("This barrier has been removed")).to_be_visible()


def test_remove_review(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)

    change_permissions(
        page,
        get_username(page),
        "Public barrier approver",
    )
    page.goto(clean_full_url(url) + "public")
    page.get_by_role("button", name="Remove approval").click()

    expect(page.get_by_text("This barrier needs to be approved again")).to_be_visible()
