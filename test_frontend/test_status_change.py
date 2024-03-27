import datetime

import pytest
from playwright.sync_api import expect

from test_frontend import PlaywrightTestBase


class TestStatusChange(PlaywrightTestBase):
    @pytest.mark.order(1)
    def test_change_status_unhappy_path(self):
        self.page.goto(self.get_barrier_detail_page())

        self.page.get_by_role("link", name="Edit status").click()
        self.page.get_by_role("button", name="Save and return").click()

        assert self.page.locator(".govuk-error-summary__title").is_visible()
        assert (
            "Select the barrier status"
            in self.page.locator(".govuk-error-summary__list").text_content()
        )

    @pytest.mark.order(2)
    def test_status_change_happy_path(self):
        self.page.goto(self.get_barrier_detail_page())

        self.page.get_by_role("link", name="Edit status").click()
        assert self.page.url.endswith("/status/")
        self.page.get_by_label("Open").check()
        self.page.get_by_label(
            "Describe briefly the status of the barrier, including recent progress and any obstacles"
        ).click()
        self.page.get_by_label(
            "Describe briefly the status of the barrier, including recent progress and any obstacles"
        ).fill("test description")
        self.page.get_by_role("button", name="Save and return").click()

        assert self.page.url == self.get_barrier_detail_page()
        assert (
            f"Barrier open on {datetime.datetime.now().strftime('%d %B %Y')}"
            in self.get_text_content_without_line_separators(
                self.page.locator(".barrier-status-details__heading").text_content()
            )
        )

        expect(self.page.locator(".barrier-status-details__text")).to_have_text(
            "test description"
        )

        # now let's change it to Resolved: In park
        self.page.get_by_role("link", name="Edit status").click()
        self.page.get_by_label("Resolved: In part").check()
        self.page.get_by_role("spinbutton", name="Day").click()
        self.page.get_by_role("spinbutton", name="Day").fill("01")
        self.page.get_by_role("spinbutton", name="Month").click()
        self.page.get_by_role("spinbutton", name="Month").fill("01")
        self.page.get_by_role("spinbutton", name="Year").click()
        self.page.get_by_role("spinbutton", name="Year").fill("2023")
        self.page.get_by_label(
            "Describe briefly how this barrier was partially resolved"
        ).click()
        self.page.get_by_label(
            "Describe briefly how this barrier was partially resolved"
        ).fill("description")
        self.page.get_by_role("button", name="Save and return").click()

        assert self.page.url == self.get_barrier_detail_page()
        assert (
            "Barrier partially resolved on 1 January 2023"
            in self.get_text_content_without_line_separators(
                self.page.locator(".barrier-status-details__heading").text_content()
            )
        )

        expect(self.page.locator(".barrier-status-details__text")).to_have_text(
            "description"
        )
