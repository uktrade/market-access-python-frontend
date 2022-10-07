from unittest.mock import Mock, patch

from django.urls import reverse
from playwright.sync_api import Page, expect

from ui_tests_playwright.settings import BASE_URL


@patch("utils.api.resources.BarriersResource.get_full_history")
def test_history_page_has_all_top_priority_items(
    mock_history: Mock, page: Page, barrier_history
):
    mock_history.return_value = barrier_history
    url = reverse(
        "barriers:history",
        kwargs={"barrier_id": "7daba55b-f421-4952-98ee-4f5b408f0af3"},
    )
    page.goto(f"{BASE_URL}{url}")
    pb100_history_items = page.locator(
        "h4.history-item__field:has-text('PB100 Priority Status')"
    )
    expect(pb100_history_items).to_have_count(5)
