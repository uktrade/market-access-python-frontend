import pytest
from playwright.sync_api import expect


@pytest.mark.order(1)
def test_tag_assignment(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    page.goto(url)

    page.get_by_role("link", name="Edit tags").click()
    page.get_by_label("Brexit").check()
    page.get_by_label("NI Protocol").check()
    page.get_by_role("button", name="Save changes").click()

    expect(page.locator(".barrier-tag-list")).to_have_count(2)

    expect(page.locator(".govuk-tag").nth(0)).to_have_text("Brexit")
    expect(page.locator(".govuk-tag").nth(1)).to_have_text("NI Protocol")


@pytest.mark.order(2)
def test_tag_removal(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    page.goto(url)
    page.get_by_role("link", name="Edit tags").click()
    page.get_by_label("Brexit").uncheck()
    page.get_by_label("NI Protocol").uncheck()
    page.get_by_role("button", name="Save changes").click()

    assert not page.locator(".barrier-tag-list").is_visible()
