import os
from .utils import get_base_url


NUM_CONCURRENT_TESTS = int(os.getenv("NUM_CONCURRENT_TESTS", 20))
HEADLESS = os.getenv("TEST_HEADLESS", "false").lower() == "true"


def test_multiple_users(context):
    # Create multiple pages with thesame session
    # to avoid the need to log in multiple times
    # since we are trying to run muliple pages on an sso session
    pages = [context.new_page() for _ in range(NUM_CONCURRENT_TESTS)]

    for page in pages:
        page.goto(f"{get_base_url()}search/")
        # perform a search
        page.get_by_role("textbox", name="Search").fill("test")
        page.get_by_text("Goods", exact=True).click()

        # Wait for the pages to load
        page.wait_for_timeout(5000)

    # Clean up after the test
    for page in pages:
        page.close()
    context.close()
