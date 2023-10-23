import logging

from django.urls import reverse
from playwright.sync_api import Page, expect

from ui_tests.settings import BASE_URL

logger = logging.getLogger(__name__)


def test_search(page: Page):
    url = reverse("barriers:dashboard", kwargs={})  # dashboard
    page.goto(f"{BASE_URL}{url}")

    button = page.locator(f"id=dash-button-1")
    expect(button).to_be_visible()

    button.click()
    expect(page).to_have_title("Market Access - Search")