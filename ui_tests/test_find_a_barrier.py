from ui_tests import settings

from .helpers.barriers import get_barrier_code, get_barrier_title


def test_find_by_title(browser):
    """
    Ensure barrier is in results when searching by barrier name
    """
    barrier_id = settings.TEST_BARRIER_ID
    title = get_barrier_title(browser, barrier_id)

    browser.visit(f"{settings.BASE_URL}find-a-barrier")
    browser.fill("search", title)
    browser.find_by_css('input[type=submit][value="Apply filters"]').first.click()
    assert browser.is_element_present_by_css(f'[data-barrier-id="{barrier_id}"]')


def test_find_by_code(browser):
    """
    Ensure barrier is in results when searching by barrier code
    """
    barrier_id = settings.TEST_BARRIER_ID
    code = get_barrier_code(browser, barrier_id)

    browser.visit(f"{settings.BASE_URL}find-a-barrier")
    browser.fill("search", code)
    browser.find_by_css('input[type=submit][value="Apply filters"]').first.click()
    assert browser.is_element_present_by_css(f'[data-barrier-id="{barrier_id}"]')


def test_priority_search_filter(browser):
    """
    Only relevant barriers should show when searching by priority
    """
    browser.visit(f"{settings.BASE_URL}find-a-barrier")

    checkbox = browser.find_by_css("input[name=priority][value='HIGH']")
    checkbox.find_by_xpath("./following-sibling::label").click()

    checkbox = browser.find_by_css("input[name=priority][value='LOW']")
    checkbox.find_by_xpath("./following-sibling::label").click()

    browser.find_by_css('input[type=submit][value="Apply filters"]').first.click()

    for result in browser.find_by_css(".filter-results-list__item"):
        priority = result.find_by_css(".priority-marker-wrapper").value
        assert priority in ("High priority", "Low priority")


def test_status_search_filter(browser):
    """
    Only relevant barriers should show when searching by status
    """
    browser.visit(f"{settings.BASE_URL}find-a-barrier")

    # Open: In progress
    checkbox = browser.find_by_css("input[name=status][value='2']")
    checkbox.find_by_xpath("./following-sibling::label").click()

    # Resolved: In full
    checkbox = browser.find_by_css("input[name=status][value='4']")
    checkbox.find_by_xpath("./following-sibling::label").click()

    browser.find_by_css('input[type=submit][value="Apply filters"]').first.click()

    for result in browser.find_by_css(".filter-results-list__item"):
        status = result.find_by_css(".barrier-status-badge").value
        assert status in ("Open: In progress", "Resolved: In full")
