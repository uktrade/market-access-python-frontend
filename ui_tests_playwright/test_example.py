from playwright.sync_api import Page, expect

from ui_tests_playwright import settings


def test_example(live_server, page: Page):
    page.goto(settings.BASE_URL)
    expect(page).to_have_title("Market Access - Homepage")
