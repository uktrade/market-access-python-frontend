from ui_tests import settings

from splinter.exceptions import ElementDoesNotExist


def remove_all_team_members(browser, barrier_id):
    for i in range(10):
        try:
            browser.find_by_css(
                ".standard-table--barrier-team .js-delete-modal"
            ).first.click()
            browser.find_by_css('input[type=submit][value="Yes, delete"]').first.click()
        except ElementDoesNotExist:
            return


def test_my_team_barriers(browser):
    """
    Check a user's team barriers appear in the search.

    Remove all members from a barrier's team, add current user to the team,
    search for 'My team barriers', ensure the barrier is in the results.

    Note: this won't work on local as that uses mocksso, and the mock user
    will not appear in the user search.
    """
    barrier_id = settings.TEST_BARRIER_ID

    browser.visit(f"{settings.BASE_URL}barriers/{barrier_id}")

    browser.click_link_by_text("Barrier team")
    remove_all_team_members(browser, barrier_id)

    browser.click_link_by_text("Add team member")
    browser.fill("query", settings.TEST_SSO_NAME)
    browser.find_by_css(".search-form button").first.click()

    browser.find_by_css(".search-card__link").first.click()

    browser.fill("role", "Test Role")
    browser.find_by_css("input[type=submit]").first.click()

    browser.visit(f"{settings.BASE_URL}find-a-barrier")
    browser.find_by_css('label[for="created_by-2"]').first.click()
    browser.find_by_css('input[type=submit][value="Apply filters"]').first.click()

    assert browser.is_element_present_by_css(f'[data-barrier-id="{barrier_id}"]')
