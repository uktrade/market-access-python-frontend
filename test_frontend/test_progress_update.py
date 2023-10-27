import pytest


from test_frontend import PlaywrightTestBase


class TestProgressUpdateCreate(PlaywrightTestBase):
    @pytest.mark.order(1)
    def test_change_status_unhappy_path(self):
        self.page.goto(self.get_barrier_detail_page())

        self.page.get_by_role("link", name="Add progress update").click()
        self.page.get_by_text("Top 100 priority barrier").click()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("On track").check()
        self.page.get_by_role("textbox", name="Provide more detail").click()
        self.page.get_by_role("textbox", name="Provide more detail").fill(
            "Playwright test"
        )
        self.page.get_by_role("button", name="Save and continue").click()
        self.page.locator("#next_step_item").click()
        self.page.locator("#next_step_item").fill("Playwright test next step")
        self.page.locator("#next_step_item").press("Tab")
        self.page.locator("#next_step_owner").fill("Playwright user")
        self.page.locator("#next_step_owner").press("Tab")
        self.page.get_by_label("Month").fill("12")
        self.page.get_by_label("Month").press("Tab")
        self.page.get_by_label("Year").fill("2023")
        self.page.get_by_role("button", name="Save").click()
        self.page.get_by_role("link", name="Confirm").click()

        assert self.page.url == self.get_barrier_detail_page()
