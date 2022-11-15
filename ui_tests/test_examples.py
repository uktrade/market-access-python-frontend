from unittest.mock import Mock, patch

from django.urls import reverse
from playwright.sync_api import Page, expect

from ui_tests import settings
from ui_tests.settings import BASE_URL


def test_example(page: Page):
    """
    Most basic example: load the root URL of the site and check the title
    N.B. This test will fail if the API isn't running
    """
    page.goto(settings.BASE_URL)
    expect(page).to_have_title("Market Access - Homepage")


def test_example_2(page: Page):
    """
    Use reverse() to get the URL path component for pages,
    but you still need BASE_URL
    N.B. This test will fail if the API isn't running
    """
    search_page_path = reverse("barriers:search")
    page.goto(f"{settings.BASE_URL}{search_page_path}")
    expect(page).to_have_title("Market Access - Search")


@patch("utils.api.resources.BarriersResource.get_full_history")
def test_example_patch_api(
    mock_history: Mock, page: Page, barrier_history, test_barrier_id
):
    """
    This example shows how to patch an API call to return a value from a fixture
    Fixtures are defined in conftest.py
    N.B. Although this successfully mocks the patched method, other API calls
         still happen, such as to /whoami.
    """
    mock_history.return_value = barrier_history
    history_path = reverse(
        "barriers:history",
        kwargs={"barrier_id": test_barrier_id},
    )
    page.goto(f"{BASE_URL}{history_path}")
    history_items = page.locator(".history-item")
    expect(history_items).to_have_count(9)