from playwright.sync_api import expect

from .utils import clean_full_url, retry


@retry()
def test_tag_assignment(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    page.goto(clean_full_url(url))

    page.get_by_role("link", name="Edit tags").click()
    page.get_by_label("Wales Priority").check()
    page.get_by_label("Europe Priority").check()
    page.get_by_role("button", name="Save changes").click()

    expect(page.locator(".barrier-tag-list")).to_have_count(2)


@retry()
def test_tag_removal(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)

    page.goto(clean_full_url(url))

    page.get_by_role("link", name="Edit tags").click()
    page.get_by_label("Brexit").uncheck()
    page.get_by_label("NI Protocol").uncheck()
    page.get_by_role("button", name="Save changes").click()

    expect(page.get_by_text("Barrier information")).to_be_visible()
