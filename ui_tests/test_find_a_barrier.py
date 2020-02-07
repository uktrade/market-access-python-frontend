from ui_tests import settings

from .helpers.barriers import get_barrier_code, get_barrier_title


def test_find_by_title(browser):
    """
    Ensure barrier is in results when searching by barrier name
    """
    barrier_id = settings.TEST_BARRIER_ID
    title = get_barrier_title(browser, barrier_id)

    browser.visit(f"{settings.BASE_URL}find-a-barrier")
    browser.fill('search', title)
    browser.find_by_css(
        'input[type=submit][value="Apply filters"]'
    ).first.click()
    assert browser.is_element_present_by_css(
        f'[data-barrier-id="{barrier_id}"]'
    )


def test_find_by_code(browser):
    """
    Ensure barrier is in results when searching by barrier code
    """
    barrier_id = settings.TEST_BARRIER_ID
    code = get_barrier_code(browser, barrier_id)

    browser.visit(f"{settings.BASE_URL}find-a-barrier")
    browser.fill('search', code)
    browser.find_by_css(
        'input[type=submit][value="Apply filters"]'
    ).first.click()
    assert browser.is_element_present_by_css(
        f'[data-barrier-id="{barrier_id}"]'
    )
