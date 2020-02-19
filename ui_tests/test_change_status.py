from ui_tests import settings

from splinter.exceptions import ElementDoesNotExist


def test_change_status(browser):
    """
    Change the status to Resolved: In part or Resolved: In full.

    Checks the new status is displayed on the barrier detail page.
    Checks the activity stream shows the change.
    Checks the Find a Barrier page shows the change.
    """
    barrier_id = settings.TEST_BARRIER_ID

    browser.visit(f"{settings.BASE_URL}barriers/{barrier_id}")

    title = browser.find_by_tag('h1').first.value

    old_status = browser.find_by_css('.barrier-status-badge').first.value
    old_status = old_status.lstrip("Status: ")

    browser.click_link_by_text('Update the barrier')
    browser.click_link_by_text('change status')

    try:
        browser.find_by_css("input[name=status][value='3']").first.click()
        new_status = "Resolved: In part"
        browser.fill('part_resolved_date_0', '1')
        browser.fill('part_resolved_date_1', '2020')
        browser.fill('part_resolved_summary', 'Test summary')
    except ElementDoesNotExist:
        browser.find_by_css("input[name=status][value='4']").first.click()
        new_status = "Resolved: In full"
        browser.fill('resolved_date_0', '1')
        browser.fill('resolved_date_1', '2020')
        browser.fill('resolved_summary', 'Test summary')

    browser.find_by_css('input[type=submit]').first.click()

    assert browser.find_by_css('.event-list__item__text').first.value == (
        f'Barrier status changed from {old_status} to {new_status} '
        f'by {settings.TEST_SSO_NAME}. Resolved date set as January 2020.'
    )
    assert browser.find_by_css('.barrier-status-badge').first.value == (
        f'Status: {new_status}'
    )

    browser.visit(f"{settings.BASE_URL}find-a-barrier/?search={title}")

    barrier_item = browser.find_by_css(
        f'[data-barrier-id="{barrier_id}"]'
    ).first
    assert barrier_item.find_by_css(
        '.barrier-status-badge'
    ).first.value == new_status
