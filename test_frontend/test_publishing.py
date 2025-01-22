from playwright.sync_api import expect

from test_frontend.conftest import create_test_barrier
from test_frontend.utils import clean_full_url, get_base_url, retry


@retry()
def test_successful_publish(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    base_url = get_base_url()
    barrier_details_url = clean_full_url(url)
    name = get_username(page, base_url, barrier_details_url)

    page.goto(barrier_details_url + "public")
    page.get_by_role("button", name="Submit for review").click()
    page.get_by_role("heading", name="This barrier is now awaiting").click()

    expect(page.get_by_text("This barrier is now awaiting approval")).to_be_visible()

    page.goto(base_url + "users")
    page.get_by_role("link", name=name).click()
    page.get_by_role("link", name="Edit profile").click()
    page.get_by_label("Public barrier approver").check()
    page.get_by_role("button", name="Save").click()

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

    page.goto(base_url + "users")
    page.get_by_role("link", name=name).click()
    page.get_by_role("link", name="Edit profile").click()
    page.get_by_label("Publisher").check()
    page.get_by_role("button", name="Save").click()

    page.goto(barrier_details_url + "public")
    page.get_by_role("link", name="Publish", exact=True).click()

    expect(
        page.get_by_text("Confirm you want to publish this barrier on GOV.UK")
    ).to_be_visible()

    if base_url != "http://market-access.local:9880/":
        page.get_by_role("button", name="Confirm").click()
        expect(
            page.get_by_text("This barrier has been published on GOV.UK")
        ).to_be_visible()


def get_username(page, base_url, barrier_details_url):
    if base_url == "http://market-access.local:9880/":
        return "Your"
    page.goto(base_url + "account")
    page.locator("dt").filter(has_text="Name").click()
    name = page.get_by_test_id("username").inner_text()
    return name
