from datetime import datetime

from ui_tests import settings

from splinter.exceptions import ElementDoesNotExist


def clear_draft_barriers(browser):
    draft_barriers_url = f"{settings.BASE_URL}reports"
    if browser.url != draft_barriers_url:
        browser.visit(draft_barriers_url)

    count = len(browser.find_by_css('.my-draft-barriers .draft-barrier-item'))

    for i in range(count):
        try:
            delete_draft_barrier(browser)
        except ElementDoesNotExist:
            return


def delete_draft_barrier(browser, index=0):
    barrier = browser.find_by_css('.draft-barrier-item')[index]
    barrier.find_by_xpath("//a[text() = 'Delete']").click()
    browser.find_by_css(
        'input[type=submit][value="Yes, delete"]'
    ).first.click()


def create_draft_barrier(
    browser,
    country_id="82756b9a-5d95-e211-a939-e4115bead28a",
):
    browser.visit(settings.BASE_URL)
    browser.click_link_by_text("Add a barrier")
    browser.click_link_by_text("Start now")

    browser.find_by_css('input[name=status][value="2"]').first.click()
    browser.find_by_css('input[type=submit]').first.click()

    browser.find_by_css('input[name=status][value="UNRESOLVED"]').first.click()
    browser.find_by_css('input[type=submit]').first.click()

    browser.select("country", country_id)
    browser.find_by_css('input[type=submit]').first.click()
    return datetime.now()
