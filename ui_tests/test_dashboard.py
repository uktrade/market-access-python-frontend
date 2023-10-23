import logging

from django.urls import reverse
from playwright.sync_api import Page, expect

from ui_tests.settings import BASE_URL

logger = logging.getLogger(__name__)

# make ui-test path=test_barrier_history.py


def test_dashboard_buttons_exist(page: Page):
    url = reverse("barriers:dashboard", kwargs={})  # dashboard
    page.goto(f"{BASE_URL}{url}")

    buttons = [1, 2, 3]  # Report, Search, Find barriers for publishing
    for button_id in buttons:
        button = page.locator(f"id=dash-button-{button_id}")
        expect(button).to_be_visible()
