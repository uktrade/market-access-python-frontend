import pytest
from playwright.sync_api import expect

from test_frontend.utils import BASE_URL, change_permissions, clean_full_url


def test_publish_general_user(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    page.goto(clean_full_url(url) + "public")
    page.get_by_role("button", name="Submit for review").click()

    expect(page.get_by_text("This barrier is now awaiting approval")).to_be_visible()


def test_publish_approver(page, create_test_barrier, is_admin, get_username):
    title = "test"
    url = create_test_barrier(title=title)
    username = get_username()
    if not is_admin():
        pytest.skip(
            f"You do not have the correct permissions to test approving barriers in {BASE_URL}"
        )
    change_permissions(
        page,
        username,
        "Public barrier approver",
    )
    page.goto(clean_full_url(url) + "public")
    page.get_by_role("link", name="Review barrier").click()
    page.locator('input[name="content_clearance"]').check()
    page.locator('input[name="external_clearances"]').check()
    page.get_by_role("button", name="Send to GOV.UK content team").click()

    expect(
        page.get_by_text(
            "This barrier has been approved and is now with the GOV.UK content team"
        )
    ).to_be_visible()
    expect(page.get_by_role("link", name="Publish", exact=True)).not_to_be_visible()

    page.get_by_role("button", name="Remove approval").click()

    expect(page.get_by_text("This barrier needs to be approved again")).to_be_visible()


def test_publish_publisher(page, create_test_barrier, is_admin, get_username):
    title = "test"
    url = create_test_barrier(title=title)
    username = get_username()
    if not is_admin():
        pytest.skip(
            f"You do not have the correct permissions to test publishing barriers in {BASE_URL}"
        )
    change_permissions(
        page,
        username,
        "Publisher",
    )
    page.goto(clean_full_url(url) + "public")
    page.get_by_role("link", name="Review barrier").click()
    page.locator('input[name="content_clearance"]').check()
    page.locator('input[name="external_clearances"]').check()
    page.get_by_role("button", name="Send to GOV.UK content team").click()
    page.get_by_role("link", name="Publish", exact=True).click()
    expect(
        page.get_by_text("Confirm you want to publish this barrier on GOV.UK")
    ).to_be_visible()

    # Barriers cannot be published on local environment
    if "local" not in BASE_URL:
        page.get_by_role("button", name="Confirm").click()

        expect(
            page.get_by_text("This barrier has been published on GOV.UK")
        ).to_be_visible()


@pytest.mark.skipif(
    "local" in BASE_URL,
    reason=f"Barriers cannot be published in {BASE_URL}",
)
def test_unpublish_publisher(page, create_test_barrier, is_admin):
    title = "test"
    url = create_test_barrier(title=title)
    if not is_admin():
        pytest.skip("You cannot publish barriers in this environment")
    page.goto(clean_full_url(url) + "public")
    page.get_by_role("link", name="Unpublish").click()
    page.locator("#id_public_publisher_summary").fill("Test")
    page.get_by_role("button", name="Confirm").click()

    expect(page.get_by_text("This barrier has been removed")).to_be_visible()
