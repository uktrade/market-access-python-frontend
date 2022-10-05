from django.urls import reverse
from playwright.sync_api import Page, expect

from ui_tests_playwright import settings


def test_example(page: Page):
    page.goto(settings.BASE_URL)
    expect(page).to_have_title("Market Access - Homepage")


def test_example_2(page: Page):
    search_page_path = reverse("barriers:search")
    page.goto(f"{settings.BASE_URL}{search_page_path}")
    expect(page).to_have_title("Market Access - Search")
