from ui_tests import settings


def get_barrier_title(browser, barrier_id):
    browser.visit(f"{settings.BASE_URL}barriers/{barrier_id}")
    return browser.find_by_tag('h1').first.value


def change_barrier_description(browser, barrier_id, new_description):
    browser.visit(f"{settings.BASE_URL}barriers/{barrier_id}")
    summary_heading = browser.find_by_text('Barrier summary').first
    summary_heading.parent.click_link_by_text('Edit')
    browser.fill('description', new_description)
    browser.find_by_css('input[type=submit]').first.click()
