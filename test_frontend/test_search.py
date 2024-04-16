from playwright.sync_api import expect

from .utils import get_base_url, retry


@retry()
def get_search_page():
    return f"{get_base_url()}search/"


@retry()
def test_search_for_a_barrier(page):

    page.goto(get_search_page())
    # remove focus on search box to allow the search results to update
    page.get_by_role("heading", name="Market access barriers Search").click()

    expect(
        page.get_by_role("heading", name="Market access barriers Search")
    ).to_be_visible()


@retry()
def test_search_for_a_barrier_with_filters(page, create_test_barrier):

    title = "test unique search 1"
    create_test_barrier(title=title)

    page.goto(get_search_page())
    page.get_by_role("textbox", name="Search").fill(title)
    page.get_by_text("Goods", exact=True).click()
    # remove focus on search box to allow the search results to update
    page.get_by_role("heading", name="Market access barriers Search").click()

    expect(page.get_by_text("Page 1 of")).to_be_visible()


@retry()
def test_saved_search(page, create_test_barrier):

    title = "test unique search"
    create_test_barrier(title=title)

    page.goto(get_search_page())
    page.get_by_role("textbox", name="Search").fill(title)
    page.get_by_text("Goods", exact=True).click()
    page.get_by_role("link", name="Save search").click()
    saved_search_name = "test saved search"
    page.get_by_label("Saved search name").fill(saved_search_name)
    page.get_by_role("button", name="Save").click()

    page.goto(get_base_url())

    # saved search tab
    page.get_by_role("link", name="My Saved searches").click()
    page.get_by_role("link", name=saved_search_name).click()

    # back to search page
    expect(page.get_by_role("link", name="Export type: Goods Activate")).to_be_visible()
