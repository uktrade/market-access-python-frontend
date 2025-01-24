from playwright.sync_api import expect

from test_frontend.utils import get_base_url, retry


@retry()
def test_update_overseas_region(page):
    page.goto(get_base_url() + "account")

    page.locator(".edit-overseas-regions").click()
    page.get_by_role("combobox").select_option("8d4c4f31-06ce-4320-8e2f-1c13559e125f")
    page.get_by_label("Add region").click()
    page.get_by_role("combobox").select_option("04a7cff0-03dd-4677-aa3c-12dd8426f0d7")
    page.get_by_label("Add region").click()
    page.get_by_role("button", name="Save and return").click()

    expect(page.locator(".overseas-regions-selection")).to_have_text(
        "Africa, Asia Pacific"
    )

    page.locator(".edit-overseas-regions").click()
    page.get_by_label("remove Africa").click()
    page.get_by_label("remove Asia Pacific").click()
    page.get_by_role("button", name="Save and return").click()

    expect(page.locator(".overseas-regions-selection")).to_have_text("None")


def test_policy_teams(page):
    page.locator(".edit-policy-teams").click()
    page.get_by_role("combobox").select_option("4")
    page.get_by_label("Add team").click()
    page.get_by_role("combobox").select_option("5")
    page.get_by_label("Add team").click()
    page.get_by_role("button", name="Save and return").click()

    expect(page.locator(".policy-teams-selection")).to_have_text(
        "Environment and climate, Gender"
    )

    page.locator(".edit-policy-teams").click()
    page.get_by_label("remove Environment and climate").click()
    page.get_by_label("remove Gender").click()
    page.get_by_role("button", name="Save and return").click()

    expect(page.locator(".policy-teams-selection")).to_have_text("None")


def test_sectors(page):
    page.locator(".edit-sectors").click()
    page.get_by_role("combobox").select_option("af959812-6095-e211-a939-e4115bead28a")
    page.get_by_label("Add sector").click()
    page.get_by_role("combobox").select_option("9838cecc-5f95-e211-a939-e4115bead28a")
    page.get_by_label("Add sector").click()
    page.get_by_role("button", name="Save and return").click()

    expect(page.locator(".sectors-selection")).to_have_text(
        "Advanced engineering, Automotive"
    )

    page.locator(".edit-sectors").click()
    page.get_by_label("remove Advanced engineering").click()
    page.get_by_label("remove Automotive").click()
    page.get_by_role("button", name="Save and return").click()

    expect(page.locator(".sectors-selection")).to_have_text("None")


def test_barrier_locations(page):
    page.locator(".edit-barrier-locations").click()
    page.get_by_role("combobox").select_option("TB00003")
    page.get_by_label("Add location").click()
    page.get_by_role("combobox").select_option("9b5f66a0-5d95-e211-a939-e4115bead28a")
    page.get_by_label("Add location").click()
    page.get_by_role("button", name="Save and return").click()

    expect(page.locator(".barrier-locations-selection")).to_have_text(
        "Antigua and Barbuda, Association of Southeast Asian Nations (ASEAN)"
    )

    page.locator(".edit-barrier-locations").click()
    page.get_by_label("remove Antigua and Barbuda").click()
    page.get_by_label("remove Association of Southeast Asian Nations (ASEAN)").click()
    page.get_by_role("button", name="Save and return").click()

    expect(page.locator(".barrier-locations-selection")).to_have_text("None")


def test_government_department(page):
    page.locator(".edit-government-department").click()
    page.get_by_role("combobox").select_option("2")
    page.get_by_role("button", name="Save and return").click()

    expect(page.locator(".government-department-selection")).to_have_text(
        "Cabinet Office"
    )

    page.locator(".edit-government-department").click()
    page.get_by_role("button", name="Save and return").click()

    expect(page.locator(".government-department-selection")).to_have_text("None")
