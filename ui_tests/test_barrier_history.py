from unittest.mock import Mock, patch

from django.urls import reverse
from playwright.sync_api import Page, expect

from ui_tests.settings import BASE_URL

# make ui-test path=test_barrier_history.py


@patch("utils.api.resources.BarriersResource.get_full_history")
def test_history_page_has_all_top_priority_items(
    mock_history: Mock, page: Page, barrier_history, test_barrier_id
):
    mock_history.return_value = barrier_history
    url = reverse(
        "barriers:history",
        kwargs={"barrier_id": test_barrier_id},
    )
    page.goto(f"{BASE_URL}{url}")
    pb100_history_items = page.locator(
        "h4.history-item__field:has-text('PB100 Priority Status')"
    )
    expect(pb100_history_items).to_have_count(5)
