import logging

from django.urls import reverse
from playwright.sync_api import Page, expect

from ui_tests.settings import BASE_URL

logger = logging.getLogger(__name__)

# make ui-test path=test_barrier_priority.py


# @patch("utils.api.resources.MarketAccessAPIClient.get")
def test_first_visit_display_initial_priority_question(page: Page, test_barrier_id):
    url = reverse("barriers:edit_priority", kwargs={"barrier_id": test_barrier_id})
    page.goto(f"{BASE_URL}{url}")
    first_form_locator = page.locator(".confirm-priority-form-section")
    second_form_locator = page.locator(".priority-form")

    content = page.content()
    logger.critical(first_form_locator)
    expect(first_form_locator).to_be_visible()
    expect(second_form_locator).to_not_be_visible()


# def test_no_priority_redirects_to_barrier_page():

# def test_yes_priority_display_secondary_questions():

# def test_barrier_has_legacy_priority_display_secondary_questions():

# def test_barrier_has_top_priority_display_secondary_questions():

# def test_barrier_
