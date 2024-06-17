import datetime
import os
import random
import string

from test_frontend.utils import clean_full_url, get_base_url

NUM_CONCURRENT_TESTS = int(os.getenv("NUM_CONCURRENT_TESTS", 50))
HEADLESS = os.getenv("TEST_HEADLESS", "false").lower() == "true"
BASE_URL = os.getenv("BASE_FRONTEND_TESTING_URL", "http://market-access.local:9880/")


def test_multiple_users(context):
    # Create multiple pages with thesame session
    # to avoid the need to log in multiple times
    # since we are trying to run muliple pages on an sso session
    pages = [context.new_page() for _ in range(NUM_CONCURRENT_TESTS)]

    for page in pages:
        page.goto(f"{get_base_url()}search/")
        page.get_by_text("Goods", exact=True).click()
        page.get_by_role("link", name="Download").click()
        page.get_by_role("link", name="Dashboard").click()

    # Clean up after the test
    for page in pages:
        page.close()


def test_multiple_barriers_add_and_update(context):
    pages = [context.new_page() for _ in range(NUM_CONCURRENT_TESTS)]

    for page in pages:
        # create a new barrier
        random_barrier_id = "".join(
            random.choice(string.ascii_uppercase) for _ in range(5)
        )
        random_barrier_name = f"test - {datetime.datetime.now().strftime('%d-%m-%Y')} - {random_barrier_id}"

        page.goto(get_base_url())
        page.get_by_role("link", name="Report a barrier").click()
        page.get_by_role("link", name="Start now").click()
        page.get_by_label("Barrier title").fill(random_barrier_name)
        page.get_by_label("Barrier description").fill("test description")
        page.get_by_role("button", name="Continue").click()
        page.locator("#status-radio-3").check()
        page.locator(
            "#status-date-group-barrier-status-partially_resolved_date_0"
        ).fill("04")
        page.locator(
            "#status-date-group-barrier-status-partially_resolved_date_1"
        ).fill("2023")
        page.locator("#id_barrier-status-partially_resolved_description").fill(
            "ifdshgihsdpihgf"
        )
        page.locator("#status-date-group-barrier-status-start_date_0").fill("03")
        page.locator("#status-date-group-barrier-status-start_date_1").fill("2024")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("combobox").select_option("TB00016")
        page.get_by_role("button", name="Continue").click()
        page.get_by_role("radio").first.check()
        page.get_by_role("button", name="Continue").click()
        page.locator("#main_sector_select").select_option(
            "9538cecc-5f95-e211-a939-e4115bead28a"
        )
        page.get_by_text("Add sector").click()
        page.locator("#sectors_select").select_option(
            "9738cecc-5f95-e211-a939-e4115bead28a"
        )
        page.locator("#sectors_select").select_option(
            "9638cecc-5f95-e211-a939-e4115bead28a"
        )
        page.get_by_role("button", name="Continue").click()
        page.get_by_placeholder("Search Company").fill("Test LTD")
        page.get_by_placeholder("Search Company").press("Enter")
        page.get_by_text("TEST LIMITEDCompanies House").click()
        page.get_by_text("Add company").click()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Goods", exact=True).check()
        page.get_by_label("Services", exact=True).check()
        page.get_by_label("Which goods, services or").fill("isfdgihisdhfgidsfg")
        page.get_by_role("button", name="Continue").click()

        # MAU extra fields
        page.get_by_label("Yes, it can be published once").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Now").check()
        page.get_by_role("button", name="Continue").click()
        page.locator("#id_barrier-public-title-title").fill("Test barrier public")
        page.locator("summary").click()
        page.get_by_role("button", name="Continue").click()
        page.locator("#id_barrier-public-summary-summary").fill("public summary")
        page.get_by_role("button", name="Continue").click()

        # save and return to barrier page
        page.get_by_role("button", name="Continue").click()
        page.wait_for_timeout(5)
        url = f'{BASE_URL}/barriers/{page.url.split("/")[-3]}/'

        # update the new barrier
        page.goto(clean_full_url(url))
        page.get_by_role("link", name="Add progress update").click()
        page.get_by_label("Barrier progress").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("On Track Barrier will be").check()
        page.get_by_label("Explain why barrier resolution is on track").fill(
            "dsghidhfgjhoighdfihjg"
        )
        page.get_by_label("Month").fill("10")
        page.get_by_label("Year", exact=True).fill("2024")
        page.get_by_role("button", name="Save and continue").click()
        page.locator("#next_step_item").fill("odhfgiuhdsoiuhdfg")
        page.locator("#next_step_owner").fill("dhfgudhsug")
        page.get_by_label("Month").fill("06")
        page.get_by_label("Year").fill("2024")
        page.get_by_role("button", name="Save").click()

        link_locator = page.get_by_role("link", name="Confirm")
        link_locator.wait_for(state="visible", timeout=60000)  # Wait up to 60 seconds
        link_locator.click()

    for page in pages:
        page.close()
