from playwright.sync_api import expect

from .utils import clean_full_url, retry, get_base_url


@retry()
def test_create_new_barrier(page):
    page.goto(clean_full_url(get_base_url()))

    page.get_by_role("button", name="Report a barrier Add a market").click()
    page.get_by_role("link", name="Start now").click()
    page.get_by_label("Barrier title").click()
    page.get_by_label("Barrier title").fill("Test barrier title")
    page.get_by_label("Barrier description").click()
    page.get_by_label("Barrier description").fill("Test barrier description")
    page.get_by_role("button", name="Continue").click()
    page.locator("#status-radio-2").check()
    page.get_by_role("spinbutton", name="Month").click()
    page.get_by_role("spinbutton", name="Month").fill("05")
    page.get_by_role("spinbutton", name="Year").click()
    page.get_by_role("spinbutton", name="Year").fill("2024")
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("combobox").select_option("TB00016")
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("radio").first.check()
    page.get_by_role("button", name="Continue").click()
    page.locator("#main_sector_select").select_option(
        "af959812-6095-e211-a939-e4115bead28a"
    )
    page.get_by_role("button", name="Continue").click()
    page.get_by_placeholder("Search Company").click()
    page.get_by_placeholder("Search Company").fill("Test LTD")
    page.locator("#search-companies-button").click()
    page.get_by_text("TEST LIMITEDCompanies House").click()
    page.get_by_text("Add company").click()
    page.get_by_role("button", name="Continue").click()
    page.get_by_label("Goods", exact=True).check()
    page.get_by_label("Which goods, services or").click()
    page.get_by_label("Which goods, services or").fill("Test test test")
    page.get_by_role("button", name="Continue").click()
    page.get_by_label("Yes, it can be published once").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_label("Now").check()
    page.get_by_role("button", name="Continue").click()
    page.locator("#id_barrier-public-title-title").click()
    page.locator("#id_barrier-public-title-title").fill("Test public title")
    page.get_by_role("button", name="Continue").click()
    page.locator("#id_barrier-public-summary-summary").click()
    page.locator("#id_barrier-public-summary-summary").fill("Test public summary")
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_role("heading", name="Barrier reported")).to_be_visible()
