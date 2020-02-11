from ui_tests import settings


def test_change_priority(browser):
    """
    Change the priority to High or Low.

    Checks the new priority is displayed on the barrier detail page.
    Checks the activity stream shows the change.
    Check the Find a Barrier page shows the change.
    """
    barrier_id = settings.TEST_BARRIER_ID

    browser.visit(f"{settings.BASE_URL}barriers/{barrier_id}")

    title = browser.find_by_tag("h1").first.value

    browser.click_link_by_text("Update the barrier")
    browser.click_link_by_text("change priority")

    current_priority = browser.find_by_css("input[checked]").first.value
    if current_priority == "HIGH":
        browser.find_by_css("input[name=priority][value=LOW]").first.click()
        new_priority_text = "Low"
    else:
        browser.find_by_css("input[name=priority][value=HIGH]").first.click()
        new_priority_text = "High"

    browser.find_by_css("input[type=submit]").first.click()

    assert browser.find_by_css(".event-list__item__text").first.value == (
        f"Barrier priority set to {new_priority_text} by Test-user."
    )
    assert browser.find_by_css(".barrier-summary__priority").first.value == (
        f"{new_priority_text} priority"
    )

    browser.visit(f"{settings.BASE_URL}find-a-barrier/?search={title}")

    barrier_item = browser.find_by_css(
        f'[data-barrier-id="{barrier_id}"]'
    ).first
    assert barrier_item.find_by_css(
        '.priority-marker-wrapper'
    ).first.value == f'{new_priority_text} priority'
