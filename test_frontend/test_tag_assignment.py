import pytest
from playwright.sync_api import expect

from test_frontend import PlaywrightTestBase


class TestTagAssignment(PlaywrightTestBase):
    @pytest.mark.order(1)
    def test_tag_assignment(self):
        self.page.goto(self.get_barrier_detail_page())
        self.page.get_by_role("link", name="Edit tags").click()
        self.page.get_by_label("Brexit").check()
        self.page.get_by_label("NI Protocol").check()
        self.page.get_by_role("button", name="Save changes").click()

        expect(self.page.locator(".barrier-tag-list")).to_have_count(2)

        expect(self.page.locator(".govuk-tag").nth(0)).to_have_text("Brexit")
        expect(self.page.locator(".govuk-tag").nth(1)).to_have_text("NI Protocol")

        self.page.close()

    @pytest.mark.order(2)
    def test_tag_removal(self):
        self.page.goto(self.get_barrier_detail_page())
        self.page.get_by_role("link", name="Edit tags").click()
        self.page.get_by_label("Brexit").uncheck()
        self.page.get_by_label("NI Protocol").uncheck()
        self.page.get_by_role("button", name="Save changes").click()

        assert not self.page.locator(".barrier-tag-list").is_visible()
