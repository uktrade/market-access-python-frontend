import random
import re

from ui_tests import settings
from .helpers.draft_barriers import (
    create_draft_barrier,
    clear_draft_barriers,
    delete_draft_barrier,
)

from dateutil import parser


def test_add_a_barrier_early_exit(browser):
    """
    Check that exiting before the location page does not create a draft barrier
    """
    clear_draft_barriers(browser)
    browser.visit(settings.BASE_URL)
    browser.click_link_by_text("Add a barrier")
    browser.click_link_by_text("Start now")

    browser.find_by_css('input[name=status][value="2"]').first.click()
    browser.find_by_css("input[type=submit]").first.click()

    browser.find_by_css('input[name=status][value="UNRESOLVED"]').first.click()
    browser.find_by_css("input[type=submit]").first.click()

    browser.click_link_by_text("Dashboard")
    browser.click_link_by_text("My draft barriers")

    draft_barriers = browser.find_by_css(".my-draft-barriers .draft-barrier-item")

    assert len(draft_barriers) == 0


def test_draft_barrier_is_created(browser):
    """
    Check that exiting after the location page creates a barrier
    """
    clear_draft_barriers(browser)

    france_id = "82756b9a-5d95-e211-a939-e4115bead28a"
    submitted_time = create_draft_barrier(browser, country_id=france_id)

    browser.visit(settings.BASE_URL)
    browser.click_link_by_text("My draft barriers")

    draft_barriers = browser.find_by_css(".my-draft-barriers .draft-barrier-item")

    assert len(draft_barriers) == 1
    assert draft_barriers.first.find_by_css("td")[2].value == "France"

    created_time = parser.parse(
        draft_barriers.first.find_by_css("td")[0].value, fuzzy=True,
    )
    # Time on page does not include seconds, so allow ~minute difference
    assert abs((created_time - submitted_time).total_seconds()) < 65

    # Test draft barrier deletion
    delete_draft_barrier(browser)
    draft_barriers = browser.find_by_css(".my-draft-barriers .draft-barrier-item")
    assert len(draft_barriers) == 0


def test_continue_draft_barrier(browser):
    clear_draft_barriers(browser)
    create_draft_barrier(browser)

    browser.visit(settings.BASE_URL)
    browser.click_link_by_text("My draft barriers")

    draft_barriers = browser.find_by_css(".my-draft-barriers .draft-barrier-item")
    draft_barriers.first.find_by_xpath("//a[text() = 'Continue']").click()

    # Check completion status for each section
    sections = browser.find_by_css(".task-list__item")
    assert sections[0].find_by_css(".task-list__item__banner").value == "COMPLETED"
    assert sections[1].find_by_css(".task-list__item__banner").value == "COMPLETED"
    assert sections[2].find_by_css(".task-list__item__banner").value == "NOT STARTED"
    assert sections[3].find_by_css(".task-list__item__banner").value == "NOT STARTED"
    assert sections[4].find_by_css(".task-list__item__banner").value == "NOT STARTED"

    # Continue adding a barrier
    browser.click_link_by_text("Continue")

    browser.find_by_css('input[name=sectors_affected][value="0"]').click()
    browser.find_by_css("input[type=submit]").click()

    title = f"Test barrier {random.randint(10000, 99999)}"
    browser.fill("barrier_title", title)
    browser.fill("product", "Product name")
    browser.choose("source", "COMPANY")
    browser.find_by_css("input[type=submit]").click()

    browser.fill("summary", "Test description")
    browser.fill("next_steps_summary", "Test next steps")
    browser.find_by_css('button[value="exit"]').click()

    # Check completion status for each section
    sections = browser.find_by_css(".task-list__item")
    assert sections[0].find_by_css(".task-list__item__banner").value == "COMPLETED"
    assert sections[1].find_by_css(".task-list__item__banner").value == "COMPLETED"
    assert sections[2].find_by_css(".task-list__item__banner").value == "COMPLETED"
    assert sections[3].find_by_css(".task-list__item__banner").value == "COMPLETED"
    assert sections[4].find_by_css(".task-list__item__banner").value == "COMPLETED"

    browser.find_by_css('input[type=submit][value="Submit barrier"]').click()

    matches = re.findall(r"/barriers/([A-Za-z0-9\-]+)", browser.url)
    assert len(matches) == 1
    barrier_id = matches[0]

    assert browser.find_by_tag("h1").first.value == title

    # Check barrier appears in 'My barriers' search
    browser.visit(f"{settings.BASE_URL}find-a-barrier")
    browser.find_by_css('label[for="user"]').first.click()
    browser.find_by_css('input[type=submit][value="Apply filters"]').first.click()
    assert browser.is_element_present_by_css(f'[data-barrier-id="{barrier_id}"]')
