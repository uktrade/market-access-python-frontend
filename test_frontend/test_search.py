from playwright.sync_api import expect

from test_frontend.utils import BASE_URL, clean_full_url, retry


@retry()
def get_search_page():
    return f"{BASE_URL}search/"


@retry()
def test_search_for_a_barrier(page):

    page.goto(get_search_page())
    # remove focus on search box to allow the search results to update
    page.get_by_role("heading", name="Market access barriers Search").click()

    expect(
        page.get_by_role("heading", name="Market access barriers Search")
    ).to_be_visible()


@retry()
def test_search_for_a_barrier_with_filters(page, create_test_barrier, session_data):

    title = session_data["barrier_title"]
    create_test_barrier(title=title)

    page.goto(get_search_page())
    page.get_by_role("textbox", name="Search").fill(title)
    page.get_by_text("Goods", exact=True).click()
    # remove focus on search box to allow the search results to update
    page.get_by_role("heading", name="Market access barriers Search").click()

    # wait for results to load
    search_results = page.get_by_role("link", name="Save search")
    search_results.wait_for(state="visible", timeout=60000)  # Wait up to 60 seconds

    expect(page.get_by_text("Page 1 of")).to_be_visible()


@retry()
def test_saved_search(page, create_test_barrier, session_data):

    title = session_data["barrier_title"]
    create_test_barrier(title=title)

    page.goto(get_search_page())
    page.get_by_role("textbox", name="Search").fill(title)
    page.get_by_text("Goods", exact=True).click()
    page.get_by_role("link", name="Save search").click()
    saved_search_name = "test saved search"
    page.get_by_label("Saved search name").fill(saved_search_name)
    page.get_by_role("button", name="Save").click()

    page.goto(BASE_URL)

    # saved search tab
    page.get_by_role("link", name="My Saved searches").click()
    page.get_by_role("link", name=saved_search_name).click()

    # back to search page
    expect(page.get_by_role("link", name="Export type: Goods Activate")).to_be_visible()


@retry()
def test_search_for_a_barrier_with_policy_name_filter(
    page, create_test_barrier, session_data
):

    title = session_data["barrier_title"]
    url = create_test_barrier(title=title)
    page.goto(clean_full_url(url))

    page.goto(get_search_page())
    page.get_by_role("group", name="Policy team").locator("svg").click()
    page.get_by_text("Gender", exact=True).click()
    # remove focus on search box to allow the search results to update
    page.get_by_role("heading", name="Market access barriers Search").click()

    # wait for results to load
    search_results = page.get_by_role("link", name="Save search")
    search_results.wait_for(state="visible", timeout=60000)  # Wait up to 60 seconds

    expect(page.get_by_text(title)).to_be_visible()
