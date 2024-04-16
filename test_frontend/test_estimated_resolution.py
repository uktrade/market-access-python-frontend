import pytest
import datetime

from .utils import clean_full_url, retry, get_text_content_without_line_separators


@retry()
@pytest.mark.order(1)
def test_estimated_resolution_change_happy_path(page, create_test_barrier):
    title = "test"
    year = str(datetime.date.today().year + 1)
    page.goto(clean_full_url(create_test_barrier(title=title)))
    page.get_by_role("link", name="Add estimated resolution date if applicable").click()
    page.get_by_label("Month").click()
    page.get_by_label("Month").fill("12")
    page.get_by_label("Year").click()
    page.get_by_label("Year").fill(year)
    page.get_by_role("button", name="Save and return").click()

    assert (
        f"Estimated resolution date 1 December {year}"
        in get_text_content_without_line_separators(
            page.locator(".summary-group__list").text_content()
        )
    )
