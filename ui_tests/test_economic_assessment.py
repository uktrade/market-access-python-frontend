from datetime import datetime, timezone

from ui_tests.helpers.barriers import create_barrier
from ui_tests import settings

from dateutil import parser


def test_economic_assessment(browser):
    """
    Check that adding an assessment creates an item in the event list.

    Note: The barrier must not already have an assessment
    """
    barrier_id = create_barrier(browser)

    barrier_detail_url = f"{settings.BASE_URL}barriers/{barrier_id}"
    if browser.url != barrier_detail_url:
        browser.visit(barrier_detail_url)

    browser.click_link_by_text("Assessment")

    browser.click_link_by_text("Add economic assessment")
    browser.choose("impact", "MEDIUMHIGH")
    browser.fill("description", "Test description")
    submitted_time = datetime.now(timezone.utc)
    browser.find_by_css("input[type=submit]").first.click()

    browser.click_link_by_text("Barrier information")
    event_list = browser.find_by_css(".event-list").first
    event_item = event_list.find_by_text("Economic assessment").find_by_xpath("../..")
    event_text = event_item.find_by_tag(".event-list__item__text").value
    assert event_text.endswith(f"added by {settings.TEST_SSO_NAME}.")

    event_time = event_item.find_by_tag("h4").value
    created_time = parser.parse(event_time, fuzzy=True)

    # Time on page does not include seconds, so allow ~minute difference
    assert abs((created_time - submitted_time).total_seconds()) < 65
