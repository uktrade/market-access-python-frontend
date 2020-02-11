import random

from ui_tests import settings

from .helpers.watchlists import create_new_watchlist


def test_save_watchlist(browser):
    """
    A saved watchlist should show the same results on the dashboard
    """
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


def test_watchlist_limit(browser):
    """
    When watchlist limit is reached, user can only replace existing watchlists
    """
    watchlist_limit = 3
    browser.visit(settings.BASE_URL)

    first_tab = browser.find_by_css('.page-tabs__tab span').first
    if first_tab.value == "My watch list":
        watchlist_count = 0
    else:
        watchlist_count = len(browser.find_by_css('.page-tabs__tab')) - 1

    # Ensure watchlist limit is reached
    for i in range(watchlist_count, watchlist_limit):
        create_new_watchlist(browser, name=f"Watchlist {i}")

    # Save a watchlist
    browser.visit(f"{settings.BASE_URL}find-a-barrier")
    checkbox = browser.find_by_css("input[name=priority][value='HIGH']")
    checkbox.find_by_xpath('./following-sibling::label').click()
    browser.find_by_css(
        'input[type=submit][value="Apply filters"]'
    ).first.click()
    browser.click_link_by_text('Save watch list')

    assert browser.is_element_not_present_by_css(
        'input[name="replace_or_new"]'
    )
    assert browser.is_element_present_by_css('input[name="replace_index"]')
