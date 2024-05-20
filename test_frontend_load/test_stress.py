import os

from test_frontend.utils import get_base_url, clean_full_url

NUM_CONCURRENT_TESTS = int(os.getenv("NUM_CONCURRENT_TESTS", 50))
HEADLESS = os.getenv("TEST_HEADLESS", "false").lower() == "true"


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
    context.close()


def test_multiple_barriers_add_and_update(context, page, create_test_barrier):
    pages = [context.new_page() for _ in range(NUM_CONCURRENT_TESTS)]

    for page in pages:
        # create a new barrier
        title = "test"
        url = create_test_barrier(title=title)
        # update the new barrier
        page.goto(clean_full_url(url))
        page.get_by_role("link", name="Add progress update").click()
        page.get_by_label("Barrier progress").check()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("On Track Barrier will be").check()
        page.get_by_label("Explain why barrier resolution is on track").click()
        page.get_by_label("Explain why barrier resolution is on track").fill(
            "dsghidhfgjhoighdfihjg"
        )
        page.get_by_label("Month").click()
        page.get_by_label("Month").fill("10")
        page.get_by_label("Year", exact=True).click()
        page.get_by_label("Year", exact=True).fill("2024")
        page.get_by_role("button", name="Save and continue").click()
        page.locator("#next_step_item").click()
        page.locator("#next_step_item").fill("odhfgiuhdsoiuhdfg")
        page.locator("#next_step_owner").click()
        page.locator("#next_step_owner").fill("dhfgudhsug")
        page.get_by_label("Month").click()
        page.get_by_label("Month").fill("06")
        page.get_by_label("Year").click()
        page.get_by_label("Year").fill("2024")
        page.get_by_role("button", name="Save").click()

        link_locator = page.get_by_role("link", name="Confirm")
        link_locator.wait_for(state="visible", timeout=60000)  # Wait up to 60 seconds
        link_locator.click()

    for page in pages:
        page.close()
    context.close()
