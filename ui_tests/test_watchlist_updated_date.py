from datetime import datetime

from ui_tests import settings

from .helpers.barriers import change_barrier_description, get_barrier_title
from .helpers.watchlists import add_watchlist_for_search_term, clear_watchlists


def test_watchlist_updated_date(browser):
    """
    Updating a field on a barrier should update 'Last updated' in watchlists
    """
    barrier_id = settings.TEST_BARRIER_ID

    clear_watchlists(browser)
    title = get_barrier_title(browser, barrier_id)
    add_watchlist_for_search_term(browser, search_term=title)
    change_barrier_description(browser, barrier_id, "Test description")
    updated_time = datetime.now()

    browser.visit(settings.BASE_URL)
    barrier_link = browser.links.find_by_partial_text(title).first
    table_row = barrier_link.find_by_xpath("../..")
    last_updated = table_row.find_by_css("td:nth-child(2)").first.value
    assert last_updated == updated_time.strftime("%-d %B %Y")
