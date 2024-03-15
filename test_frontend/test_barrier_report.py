import pytest

from playwright.sync_api import expect

from test_frontend import PlaywrightTestBase

class TestBarrierReport(PlaywrightTestBase):

    @classmethod
    def get_barrier_page(cls):
        return f"{cls.base_url}/barriers/{cls.TEST_BARRIER_ID}/"

    @pytest.mark.order(1)
    def test_report_a_barrier(self):
        self.page.goto(f"{self.base_url}")
        self.page.get_by_role("button", name="Report a barrier Add a market").click()

        assert self.page.url == f"{self.base_url}/barriers/report-a-barrier/"

    @pytest.mark.order(2)
    def test_change_barrier_priority(self):
        self.page.goto(self.get_barrier_page())
        self.page.get_by_role("link", name="Activate link to change").click()
        self.page.locator("#confirm-priority-yes").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("Top 100 priority barrier Barrier needs significant input from DBT policy teams").check()
        self.page.get_by_label("Describe why this should be").click()
        self.page.get_by_label("Describe why this should be").fill("this is a top 100 priority barrier")
        self.page.get_by_role("button", name="Save and return").click()

        assert self.page.url == self.get_barrier_page()

    @pytest.mark.order(2)
    def test_change_top_100_status(self):
        self.page.goto(self.get_barrier_page())

        # add tag top 100 priority
        self.page.get_by_role("link", name="Edit tags").click()
        self.page.get_by_label("Programme Fund").check()
        self.page.get_by_label("Scoping (Top 100 priority").check()
        self.page.get_by_role("button", name="Save changes").click()

        # change status to top 100 priority
        self.page.get_by_role("link", name="Add progress update").click()
        self.page.get_by_label("Barrier progress").check()
        self.page.get_by_role("button", name="Continue").click()
        self.page.get_by_label("On Track Barrier will be").check()
        self.page.get_by_label("Explain why barrier resolution is on track").click()
        self.page.get_by_label("Explain why barrier resolution is on track").fill("because it is being resolved")
        self.page.get_by_label("Month").click()
        self.page.get_by_label("Month").fill("10")
        self.page.get_by_label("Year", exact=True).click()
        self.page.get_by_label("Year", exact=True).fill("2024")
        self.page.get_by_role("button", name="Save and continue").click()
        self.page.locator("#next_step_item").click()
        self.page.locator("#next_step_item").fill("check documents")
        self.page.locator("#next_step_owner").click()
        self.page.locator("#next_step_owner").fill("the next investigator")
        self.page.get_by_label("Month").click()
        self.page.get_by_label("Month").fill("8")
        self.page.get_by_label("Year").click()
        self.page.get_by_label("Year").fill("2024")
        self.page.get_by_role("button", name="Save").click()

        expect(self.page.get_by_text("On track")).to_be_visible()

    @pytest.mark.order(3)
    def test_add_tag(self):
        self.page.goto(self.get_barrier_page())
        self.page.get_by_role("link", name="Edit tags").click()
        self.page.get_by_label("Programme Fund").check()
        self.page.get_by_label("Scoping (Top 100 priority").check()
        self.page.get_by_role("button", name="Save changes").click()

        assert self.page.url == self.get_barrier_page()

    @pytest.mark.order(5)
    def test_update_sector(self):
        self.page.goto(self.get_report_a_barrier_page())
        self.page.get_by_label("edit main sector").click()
        self.page.get_by_role("combobox").select_option("9738cecc-5f95-e211-a939-e4115bead28a")
        self.page.get_by_role("button", name="Add main sector").click()

        expect(self.page.locator(".summary-group__list__value__list__item")).to_have_text("Aerospace")

    @pytest.mark.order(6)
    def test_add_team_member(self):
        self.page.goto(self.get_report_a_barrier_page())
        self.page.get_by_role("link", name="Add team member").click()
        self.get_by_placeholder("Search for user").click()
        self.get_by_placeholder("Search for user").fill("Johnny")
        self.get_by_role("button", name="Search").click()
        self.get_by_role("button", name="Add Johnny Wehner").click()
        self.get_by_role("link", name="Add team member").click()

        assert self.page.url == self.get_barrier_page()
