import pytest
from playwright.sync_api import expect
from .utils import clean_full_url, retry


@retry()
@pytest.mark.order(1)
def test_change_top_100_status(page, create_test_barrier):

    title = "test"
    url = create_test_barrier(title=title)
    page.goto(clean_full_url(url))

    # add tag top 100 priority
    page.get_by_role("link", name="Edit tags").click()
    page.get_by_label("Programme Fund").check()
    page.get_by_label("Scoping (Top 100 priority").check()
    page.get_by_role("button", name="Save changes").click()

    expect(page.get_by_text("Barrier information")).to_be_visible()
