from ui_tests import settings


def test_find_a_barrier(browser):
    browser.visit(f"{settings.BASE_URL}find-a-barrier/")
    heading = browser.find_by_tag('h1').first
    assert "Find a barrier" in heading.value
