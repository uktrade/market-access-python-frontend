import logging

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

    submit_button.click()

    priority_summary_rejection = page.locator("id=priority_summary-rejection")

    expect(priority_summary_rejection).to_be_visible()


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

    # submit form
    submit_priority_form_button = page.locator("id=submit-priority-form")

    with page.expect_navigation() as redirect:
        submit_priority_form_button.submit()

    # Expect to be redirected to the barrier details page
    redirect_url = redirect.value.request.url
    assert redirect_url == f"{BASE_URL}/barriers/{test_barrier_id}/"
