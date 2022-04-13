from ui_tests import settings


def test_add_a_barrier(browser):
    """
    Check that exiting before the location page does not create a draft barrier
    """
    browser.visit(settings.BASE_URL)
    browser.find_by_css(".dash-button").first.click()
    browser.click_link_by_text("Start now")

    browser.find_by_css('input[value="2"]').first.click()
    browser.find_by_css("input[type=submit]").first.click()

    browser.find_by_css('input[value="2"]').first.click()
    browser.find_by_name("open_in_progress_summary").first.fill("Test description")
    browser.find_by_css("input[type=submit]").first.click()

    browser.find_by_id("location").select("a75f66a0-5d95-e211-a939-e4115bead28a")
    browser.find_by_css("input[type=submit]").first.click()

    browser.find_by_css('input[value="yes"]').first.click()
    browser.find_by_css("input[type=submit]").first.click()

    browser.find_by_css('input[value="1"]').first.click()
    browser.find_by_css("input[type=submit]").first.click()

    browser.find_by_css('input[value="0"]').first.click()
    browser.find_by_css("input[type=submit]").first.click()

    browser.find_by_name("title").fill("Test title")
    browser.find_by_name("product").fill("Test product")
    browser.find_by_css('input[name="source"][value="TRADE"]').first.click()
    browser.find_by_css("input[type=submit]").first.click()

    browser.find_by_name("summary").fill("Test description")
    browser.find_by_css('input[value="no"]').first.click()
    browser.find_by_name("next_steps_summary").fill("Test next steps summary")
    browser.find_by_css("input[type=submit]").first.click()

    assert (
        browser.find_by_css(".barrier-summary__heading__text").first.value
        == "Test title"
    )

    browser.click_link_by_text("Dashboard")
