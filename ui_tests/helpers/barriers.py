import random
import re

from ui_tests import settings


def get_barrier_code(browser, barrier_id):
    detail_url = f"{settings.BASE_URL}barriers/{barrier_id}"
    if browser.url != detail_url:
        browser.visit(detail_url)
    heading = browser.find_by_css(".barrier-summary__heading").value
    return heading.split("\n")[0]


def get_barrier_title(browser, barrier_id):
    detail_url = f"{settings.BASE_URL}barriers/{barrier_id}"
    if browser.url != detail_url:
        browser.visit(detail_url)
    return browser.find_by_tag("h1").first.value


def change_barrier_description(browser, barrier_id, new_description):
    browser.visit(f"{settings.BASE_URL}barriers/{barrier_id}")
    summary_heading = browser.find_by_text("Barrier summary").first
    summary_heading.parent.click_link_by_text("Edit")
    browser.fill("description", new_description)
    browser.find_by_css("input[type=submit]").first.click()


def create_barrier(browser):
    """
    Create a barrier by going through the 'add a barrier' flow
    """
    browser.visit(settings.BASE_URL)

    browser.click_link_by_text("Add a barrier")
    browser.click_link_by_text("Start now")

    browser.find_by_css('input[name=status][value="2"]').first.click()
    browser.find_by_css("input[type=submit]").first.click()

    browser.find_by_css('input[name=status][value="UNRESOLVED"]').first.click()
    browser.find_by_css("input[type=submit]").first.click()

    country_id = "82756b9a-5d95-e211-a939-e4115bead28a"
    browser.select("country", country_id)
    browser.find_by_css("input[type=submit]").first.click()

    browser.find_by_css('input[name=sectors_affected][value="0"]').click()
    browser.find_by_css("input[type=submit]").click()

    title = f"Test barrier {random.randint(10000, 99999)}"
    browser.fill("barrier_title", title)
    browser.fill("product", "Product name")
    browser.choose("source", "COMPANY")
    browser.find_by_css("input[type=submit]").click()

    browser.fill("summary", "Test description")
    browser.fill("next_steps_summary", "Test note")
    browser.find_by_css("input[type=submit]").click()

    matches = re.findall(r"/barriers/([A-Za-z0-9\-]+)", browser.url)
    barrier_id = matches[0]
    return barrier_id
