import pytest

from playwright.sync_api import expect

from test_frontend import PlaywrightTestBase

class TestSearch(PlaywrightTestBase):

    @classmethod
    def get_search_page(cls):
        return f"{cls.base_url}/search/"

    @pytest.mark.order(1)
    def test_search_for_a_barrier(self):
        self.create_test_barrier(title="test 2")
        self.page.goto(self.get_search_page())
        # remove focus on search box to allow the search results to update
        self.page.get_by_role("heading", name="Market access barriers Search").click()

        expect(self.page.get_by_role("heading", name="2barriers")).to_be_visible()

    @pytest.mark.order(2)
    def test_search_for_a_barrier_with_filters(self):
        self.create_test_barrier(title="test 2")
        self.page.goto(self.get_search_page())
        self.page.get_by_role("textbox", name="Search").fill("test 2")
        self.page.get_by_text("Goods").click()
        # remove focus on search box to allow the search results to update
        self.page.get_by_role("heading", name="Market access barriers Search").click()

        expect(self.page.get_by_role("heading", name="1barrier")).to_be_visible()


    @pytest.mark.order(3)
    def test_saved_search(self):
        self.create_test_barrier(title="test 2")
        self.page.goto(self.get_search_page())
        self.page.get_by_role("textbox", name="Search").fill("test 2")
        self.page.get_by_role("link", name="Save search").click()
        saved_search_name = "test saved search"
        self.page.get_by_label("Saved search name").fill(saved_search_name)
        self.page.get_by_role("button", name="Save").click()

        assert f"{self.get_search_page()}?search_id=" in self.page.url

        self.page.goto(self.base_url)

        # saved search tab
        self.page.get_by_role("link", name="My Saved searches").click()
        self.page.get_by_role("link", name=saved_search_name).click()

        # back to search page
        assert self.page.locator(".filter-results-title .filter-results-header__row-item").inner_text() == "1"
        expect(self.page.get_by_role("heading", name="1barrier")).to_be_visible()
