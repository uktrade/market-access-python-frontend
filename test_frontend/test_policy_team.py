from playwright.sync_api import expect

from test_frontend.utils import clean_full_url, retry


@retry()
def test_add_policy_team(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    page.goto(clean_full_url(url))

    page.get_by_role("link", name="Add a policy team").click()
    page.get_by_role("link", name="Add a policy team").click()
    page.get_by_label("Customs").check()
    page.get_by_role("button", name="Add").click()
    page.get_by_role("button", name="Save and return").click()
    page.get_by_text("Customs").click()

    expect(page.locator(".policy-teams_text")).to_have_text("Customs")


def test_update_policy_team(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    page.goto(clean_full_url(url))

    page.get_by_label("edit policy teams").click()
    page.get_by_role("link", name="Add a policy team").click()
    page.get_by_label("Gender").check()
    page.get_by_role("button", name="Add").click()
    page.get_by_role("button", name="Save and return").click()

    expect(page.locator(".policy-teams_text")).to_have_text("Customs\nGender")

    page.get_by_label("edit policy teams").click()
    page.get_by_label("Submit form to remove Customs.").click()
    page.get_by_role("button", name="Save and return").click()

    expect(page.locator(".policy-teams_text")).to_have_text("Gender")


def test_policy_team_history(page, create_test_barrier):
    title = "test"
    url = create_test_barrier(title=title)
    page.goto(clean_full_url(url))

    page.get_by_role("link", name="History").click()

    expect(page.get_by_text("old value: Customs, Gender")).to_be_visible()
    expect(page.get_by_text("new value: Gender")).to_be_visible()
