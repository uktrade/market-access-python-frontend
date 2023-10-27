import datetime
import os
import random
import re
import string

from django.conf import settings
from django.test.testcases import TransactionTestCase
from playwright.sync_api import sync_playwright


class PlaywrightTestBase(TransactionTestCase):
    create_new_test_barrier = True
    base_url = settings.BASE_FRONTEND_TESTING_URL

    @classmethod
    def setUpClass(cls):
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=settings.HEADLESS)

        if cls.create_new_test_barrier:
            cls.create_test_barrier()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    @property
    def barrier_detail_page(self):
        return f"{self.base_url}/barriers/{self.TEST_BARRIER_ID}/"

    @classmethod
    def create_test_barrier(cls):
        new_browser = cls.playwright.chromium.launch(headless=True)
        context = new_browser.new_context()
        page = context.new_page()

        random_barrier_id = "".join(
            random.choice(string.ascii_uppercase) for i in range(5)
        )
        random_barrier_name = f"test title - {datetime.datetime.now().strftime('%d-%m-%Y')} - {random_barrier_id}"

        page.goto(cls.base_url)
        page.get_by_role("link", name="Report a barrier").click()
        page.get_by_role("link", name="Start now").click()
        page.get_by_label("Barrier title").click()
        page.get_by_label("Barrier title").fill(random_barrier_name)
        page.get_by_label("Barrier description").click()
        page.get_by_label("Barrier description").click()
        page.get_by_label("Barrier description").fill("test description")
        page.get_by_role("button", name="Continue").click()

        page.locator("#status-radio-2").check()
        page.get_by_role("spinbutton", name="Month").click()
        page.get_by_role("spinbutton", name="Month").fill("03")
        page.get_by_role("spinbutton", name="Month").press("Tab")
        page.get_by_role("spinbutton", name="Year").fill("2012")
        page.get_by_role("button", name="Continue").click()
        page.locator('select[name="barrier-location-location_select"]').select_option(
            "955f66a0-5d95-e211-a939-e4115bead28a"
        )
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Importing or investing into the UK").check()
        page.get_by_role("button", name="Continue").click()
        page.locator("#main_sector_select").select_option(
            "9a38cecc-5f95-e211-a939-e4115bead28a"
        )
        page.get_by_text("Add sector").click()
        page.locator("#sectors_select").select_option(
            "a038cecc-5f95-e211-a939-e4115bead28a"
        )
        page.get_by_text("Add sector").click()
        page.get_by_text("Add sector").click()
        page.locator("#sectors_select").select_option(
            "ac22c9d2-5f95-e211-a939-e4115bead28a"
        )
        page.get_by_text("Add sector").click()
        page.get_by_role("button", name="Continue").click()
        page.get_by_placeholder("Search Company").click()
        page.get_by_placeholder("Search Company").fill("test")
        page.locator("#search-companies-button").click()
        page.get_by_text(
            "TEST LIMITEDCompanies House number 04301762Companies Name TEST LIMITEDIncorporat"
        ).click()
        page.get_by_text("Add company").click()
        page.get_by_text("Add another company").click()
        page.get_by_placeholder("Search Company").click()
        page.get_by_placeholder("Search Company").fill("test")
        page.locator("#search-companies-button").click()
        page.get_by_text(
            "TEST ALL COLOUR LIMITEDCompanies House number 11661135Companies Name TEST ALL CO"
        ).click()
        page.get_by_text("Add company").click()
        page.get_by_role("button", name="Continue").click()
        page.get_by_label("Goods", exact=True).check()
        page.get_by_label(
            "Which goods, services or investments does the barrier affect?"
        ).click()
        page.get_by_label(
            "Which goods, services or investments does the barrier affect?"
        ).fill("enter all goods")

        page.get_by_role("button", name="Continue").click()
        page.locator("#continue-button").click()

        cls.TEST_BARRIER_ID = page.url.split("/")[-3]

        context.close()
        new_browser.close()

    def get_text_content_without_line_separators(self, text_content):
        text_content = text_content.replace("\n", "")
        text_content = text_content.replace("\r", "")
        text_content = re.sub(r"\s+", " ", text_content)
        return text_content
