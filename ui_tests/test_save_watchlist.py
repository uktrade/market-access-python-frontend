import random

from ui_tests import settings


def test_save_watchlist(browser):
    """
    A saved watchlist should show the same results on the dashboard
    """
    barrier_id = settings.TEST_BARRIER_ID

    browser.visit(f"{settings.BASE_URL}find-a-barrier")

    checkbox = browser.find_by_css("input[name=priority][value='UNKNOWN']")
    checkbox.find_by_xpath('./following-sibling::label').click()

    checkbox = browser.find_by_css("input[name=status][value='2']")
    checkbox.find_by_xpath('./following-sibling::label').click()

    browser.find_by_css(
        'input[type=submit][value="Apply filters"]'
    ).first.click()

    result_count_text = browser.find_by_css('.filter-results-title').value

    browser.click_link_by_text('Save watch list')

    watchlist_name = f"Test watchlist {random.randint(1000, 9999)}"
    browser.fill('name', watchlist_name)

    browser.choose('replace_or_new', 'replace')
    browser.choose('replace_index', '0')

    browser.find_by_css('input[type=submit]').first.click()

    active_tab = browser.find_by_css('.page-tabs__tab--active span')

    if active_tab.value != watchlist_name:
        browser.click_link_by_text(watchlist_name)

    watchlist_header = browser.find_by_css('.dashboard-results-header__title')
    assert watchlist_header.value == result_count_text
