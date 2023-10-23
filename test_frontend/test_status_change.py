import datetime

from playwright.sync_api import expect

from test_frontend import PlaywrightTestBase


class TestStatusChange(PlaywrightTestBase):
    def test_change_status_unhappy_path(self):
        page = self.browser.new_page()
        page.goto(self.barrier_detail_page)

        page.get_by_role("link", name="Edit status").click()
        page.get_by_role("button", name="Save and return").click()

        assert page.locator(".govuk-error-summary__title").is_visible()
        assert (
            "Select the barrier status"
            in page.locator(".govuk-error-summary__list").text_content()
        )
        page.close()

    def test_status_change_happy_path(self):
        page = self.browser.new_page()
        page.goto(self.barrier_detail_page)

        page.get_by_role("link", name="Edit status").click()
        assert page.url.endswith("/status/")
        page.get_by_label("Open").check()
        page.get_by_label(
            "Describe briefly the status of the barrier, including recent progress and any obstacles"
        ).click()
        page.get_by_label(
            "Describe briefly the status of the barrier, including recent progress and any obstacles"
        ).fill("test description")
        page.get_by_role("button", name="Save and return").click()

        assert page.url == self.barrier_detail_page
        assert (
            f"Barrier open on {datetime.datetime.now().strftime('%d %B %Y')}"
            in self.get_text_content_without_line_separators(
                page.locator(".barrier-status-details__heading").text_content()
            )
        )

        expect(page.locator(".barrier-status-details__text")).to_have_text(
            "test description"
        )

        # now let's change it to Resolved: In park
        page.get_by_role("link", name="Edit status").click()
        page.get_by_label("Resolved: In part").check()
        page.get_by_role("spinbutton", name="Day").click()
        page.get_by_role("spinbutton", name="Day").fill("01")
        page.get_by_role("spinbutton", name="Month").click()
        page.get_by_role("spinbutton", name="Month").fill("01")
        page.get_by_role("spinbutton", name="Year").click()
        page.get_by_role("spinbutton", name="Year").fill("2023")
        page.get_by_label(
            "Describe briefly how this barrier was partially resolved"
        ).click()
        page.get_by_label(
            "Describe briefly how this barrier was partially resolved"
        ).fill("description")
        page.get_by_role("button", name="Save and return").click()

        assert page.url == self.barrier_detail_page
        assert (
            "Barrier partially resolved on 1 January 2023"
            in self.get_text_content_without_line_separators(
                page.locator(".barrier-status-details__heading").text_content()
            )
        )

        expect(page.locator(".barrier-status-details__text")).to_have_text(
            "description"
        )

        page.close()
