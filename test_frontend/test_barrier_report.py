from playwright.sync_api import expect

from .utils import clean_full_url, get_base_url, retry


@retry()
def test_report_a_barrier_page(page):
    page.goto(clean_full_url(get_base_url()))
    page.get_by_role("button", name="Report a barrier Add a market").click()
    expect(
        page.get_by_role("heading", name="Market access barriers Report")
    ).to_be_visible()


@retry()
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


@retry()
def test_add_tag(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    page.goto(clean_full_url(url))

    page.get_by_role("link", name="Edit tags").click()
    page.get_by_label("Programme Fund - Facilitative Regional", exact=True).check()
    page.get_by_label("Scoping (Top 100 priority").check()
    page.get_by_role("button", name="Save changes").click()


@retry()
def test_update_sector(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    page.goto(clean_full_url(url), wait_until="load")

    page.get_by_label("edit main sector").click()
    page.get_by_role("combobox").select_option("9b38cecc-5f95-e211-a939-e4115bead28a")
    page.get_by_role("button", name="Add main sector").click()
    page.get_by_text("Chemicals").click()
    expect(page.get_by_text("Chemicals")).to_be_visible()
