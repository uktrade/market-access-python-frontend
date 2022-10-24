import logging

from django.urls import reverse
from playwright.sync_api import Page, expect

from ui_tests.settings import BASE_URL

# from unittest.mock import Mock, patch


logger = logging.getLogger(__name__)

# make ui-test path=test_barrier_priority.py

# @patch("utils.api.resources.BarriersResource.get_full_history")
# def test_history_page_has_all_top_priority_items(
#    mock_history: Mock, page: Page, barrier_history
# ):
#    mock_history.return_value = barrier_history
#    url = reverse(
#        "barriers:history",
#        kwargs={"barrier_id": "7daba55b-f421-4952-98ee-4f5b408f0af3"},
#    )
#    page.goto(f"{BASE_URL}{url}")
#    pb100_history_items = page.locator(
#        "h4.history-item__field:has-text('PB100 Priority Status')"
#    )
#    expect(pb100_history_items).to_have_count(5)


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


# barriers/<uuid:barrier_id>/edit/priority/

# def test_no_priority_redirects_to_barrier_page():

# def test_yes_priority_display_secondary_questions():

# def test_barrier_has_legacy_priority_display_secondary_questions():

# def test_barrier_has_top_priority_display_secondary_questions():

# def test_barrier_
