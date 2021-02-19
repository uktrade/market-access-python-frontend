from splinter.exceptions import ElementDoesNotExist

from ui_tests import settings


def clear_watchlists(browser):
    browser.visit(settings.BASE_URL)

    for i in range(5):
        try:
            browser.click_link_by_text("Manage list")
            browser.click_link_by_text(" Delete list ")
        except ElementDoesNotExist:
            return


def add_watchlist_for_search_term(browser, search_term):
    browser.visit(f"{settings.BASE_URL}search/?search={search_term}")

    browser.click_link_by_text("Save watch list")

    browser.fill("name", "Test Watchlist")
    browser.find_by_css("input[type=submit]").first.click()


def create_new_watchlist(browser, name):
    browser.visit(f"{settings.BASE_URL}search/?search=test")

    browser.click_link_by_text("Save watch list")

    browser.fill("name", name)
    browser.choose("replace_or_new", "new")
    browser.find_by_css("input[type=submit]").first.click()
