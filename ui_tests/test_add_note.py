import random
import string

from ui_tests import settings


def test_add_note(browser):
    """
    A saved note should appear in the event list on the barrier detail page
    """
    barrier_id = settings.TEST_BARRIER_ID

    browser.visit(f"{settings.BASE_URL}barriers/{barrier_id}")

    browser.click_link_by_text('Add note')

    random_string = ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=32)
    )
    browser.fill('note', random_string)
    browser.find_by_css('input[type=submit][value="Save note"]').first.click()
    note_item = browser.find_by_css('.event_list__item--note').first
    note_text = note_item.find_by_css('.event-list__item__text').value
    assert note_text == random_string
