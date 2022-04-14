from splinter import Browser

from ui_tests import settings


def test_login(browser: Browser):
    browser.visit(f"{settings.BASE_URL}")
    h1 = browser.find_by_css("h1")
    assert h1.text == "Market access barriers\nDashboard"
