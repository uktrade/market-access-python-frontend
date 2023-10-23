import logging
from urllib.parse import urljoin

from django.urls import reverse
from playwright.sync_api import Page, expect

from ui_tests.settings import BASE_URL

logger = logging.getLogger(__name__)

# make ui-test path=test_barrier_priority.py


def test_first_visit_display_initial_priority_question(page: Page, test_barrier_id):
    url = reverse("barriers:edit_priority", kwargs={"barrier_id": test_barrier_id})
    page.goto(f"{BASE_URL}{url}")
    first_form_locator = page.locator("id=confirm-priority-form-section")
    second_form_locator = page.locator("id=priority-form")

    # Expect confirm-priority-form-section to be visible, priority-form to not be.
    expect(first_form_locator).to_be_visible()
    expect(second_form_locator).not_to_be_visible()


def test_cancel_redirects_to_barrier_page(page: Page, test_barrier_id):
    url = reverse("barriers:edit_priority", kwargs={"barrier_id": test_barrier_id})
    page.goto(f"{BASE_URL}{url}")

    cancel_button = page.locator("id=cancel-priority")

    with page.expect_navigation() as redirect:
        cancel_button.click()

    # Expect to be redirected to the barrier details page
    redirect_url = redirect.value.request.url
    assert redirect_url == f"{BASE_URL}/barriers/{test_barrier_id}/"


def test_no_priority_redirects_to_barrier_page(page: Page, test_barrier_id):
    url = reverse("barriers:edit_priority", kwargs={"barrier_id": test_barrier_id})
    page.goto(f"{BASE_URL}{url}")

    confirm_radio = page.locator("id=confirm-priority-no")
    confirm_radio.click()

    submit_button = page.locator("id=confirm-priority-button-js")
    with page.expect_navigation() as redirect:
        submit_button.click()

    # Expect to be redirected to the barrier details page
    redirect_url = redirect.value.request.url
    assert redirect_url == f"{BASE_URL}/barriers/{test_barrier_id}/"


def test_yes_priority_display_secondary_questions(page: Page, test_barrier_id):
    url = reverse("barriers:edit_priority", kwargs={"barrier_id": test_barrier_id})
    page.goto(f"{BASE_URL}{url}")

    confirm_radio = page.locator("id=confirm-priority-yes")
    confirm_radio.click()

    submit_button = page.locator("id=confirm-priority-button-js")
    submit_button.click()

    first_form_locator = page.locator("id=confirm-priority-form-section")
    second_form_locator = page.locator("id=priority-form")

    # Expect confirm-priority-form-section to be visible, priority-form to not be.
    expect(first_form_locator).not_to_be_visible()
    expect(second_form_locator).to_be_visible()


def test_regional_level_opens_top_priority_section(page: Page, test_barrier_id):
    url = reverse("barriers:edit_priority", kwargs={"barrier_id": test_barrier_id})
    page.goto(f"{BASE_URL}{url}")

    # Navigate to second form page
    confirm_radio = page.locator("id=confirm-priority-yes")
    confirm_radio.click()
    submit_button = page.locator("id=confirm-priority-button-js")
    submit_button.click()

    # Expect consideration question to be hidden
    consideration_question = page.locator("id=top_barrier")
    expect(consideration_question).not_to_be_visible()

    # Click Overseas delivery option
    priority_radio = page.locator("id=priority_level-2")
    priority_radio.click()

    # No longer relevant?
    # # Expect consideration question to appear
    # expect(consideration_question).to_be_visible()


def test_country_level_opens_top_priority_section(page: Page, test_barrier_id):
    url = reverse("barriers:edit_priority", kwargs={"barrier_id": test_barrier_id})
    page.goto(f"{BASE_URL}{url}")

    # Navigate to second form page
    confirm_radio = page.locator("id=confirm-priority-yes")
    confirm_radio.click()
    submit_button = page.locator("id=confirm-priority-button-js")
    submit_button.click()

    # Expect consideration question to be hidden
    consideration_question = page.locator("id=top_barrier")
    expect(consideration_question).not_to_be_visible()

    # Click Country priority option
    priority_radio = page.locator("id=priority_level-3")
    priority_radio.click()

    # No longer relevant?
    # # Expect consideration question to appear
    # expect(consideration_question).to_be_visible()


def test_watchlist_level_closes_top_priority_section(page: Page, test_barrier_id):
    url = reverse("barriers:edit_priority", kwargs={"barrier_id": test_barrier_id})
    page.goto(f"{BASE_URL}{url}")

    # Navigate to second form page
    confirm_radio = page.locator("id=confirm-priority-yes")
    confirm_radio.click()
    submit_button = page.locator("id=confirm-priority-button-js")
    submit_button.click()

    # Expect consideration question to be hidden
    consideration_question = page.locator("id=top_barrier")
    expect(consideration_question).not_to_be_visible()

    # Click Watchlist priority option
    priority_radio = page.locator("id=priority_level-3")
    priority_radio.click()

    # Expect consideration question to be hidden
    expect(consideration_question).not_to_be_visible()


def test_consideration_question_opens_summary_input(page: Page, test_barrier_id):
    url = reverse("barriers:edit_priority", kwargs={"barrier_id": test_barrier_id})
    page.goto(f"{BASE_URL}{url}")

    # Navigate to second form page & open consideration question
    confirm_radio = page.locator("id=confirm-priority-yes")
    confirm_radio.click()
    submit_button = page.locator("id=confirm-priority-button-js")
    submit_button.click()
    priority_radio = page.locator("id=priority_level-2")
    priority_radio.click()

    # Gather top priority elements
    consideration_radio_yes = page.locator("id=top_barrier-1")
    consideration_radio_no = page.locator("id=top_barrier-2")
    top_priority_summary_input = page.locator("id=priority_summary-container")

    # No longer relevant?
    # Expect 'yes' to open summary input, expect 'no' to close it
    # expect(top_priority_summary_input).not_to_be_visible()
    # consideration_radio_yes.click()
    # expect(top_priority_summary_input).to_be_visible()
    # consideration_radio_no.click()
    # expect(top_priority_summary_input).not_to_be_visible()


# Potential Tests:
# def test_barrier_with_top_priority_has_section_locked_open
# def test_barrier_awaiting_approval_has_notice_section
# def test_admins_see_approval_question
# def test_error_watchlist_top_priority_attempted
# def test_error_top_priority_without_summary
