from playwright.sync_api import expect


def test_dashboard_page(page):
    expect(page.get_by_role("link", name="Barriers I have created")).to_be_visible()
