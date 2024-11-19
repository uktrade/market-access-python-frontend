from core.tests import MarketAccessTestCase
from users.account.forms import (
    UserEditBarrierLocationsForm,
    UserEditGovernmentDepartmentForm,
    UserEditOverseasRegionsForm,
    UserEditPolicyTeamsForm,
    UserEditSectorsForm,
)


class AccountHomeFormsTestCase(MarketAccessTestCase):
    def check_for_valid_form(self, form, data, response):
        form = form(
            {
                "form": data,
            }
        )
        assert form.is_valid()
        assert form.cleaned_data["form"] == response

    def test_valid_form_overseas_regions(self):
        self.check_for_valid_form(
            UserEditOverseasRegionsForm,
            """[
                "04a7cff0-03dd-4677-aa3c-12dd8426f0d7",
                "8d4c4f31-06ce-4320-8e2f-1c13559e125f"
            ]""",
            [
                "04a7cff0-03dd-4677-aa3c-12dd8426f0d7",
                "8d4c4f31-06ce-4320-8e2f-1c13559e125f",
            ],
        )

    def test_valid_form_no_overseas_regions(self):
        self.check_for_valid_form(
            UserEditOverseasRegionsForm,
            """[]""",
            [],
        )

    def test_valid_form_policy_teams(self):
        self.check_for_valid_form(
            UserEditPolicyTeamsForm,
            """["1","5"]""",
            ["1", "5"],
        )

    def test_valid_form_no_policy_teams(self):
        self.check_for_valid_form(
            UserEditPolicyTeamsForm,
            """[]""",
            [],
        )

    def test_valid_form_sectors(self):
        self.check_for_valid_form(
            UserEditSectorsForm,
            """[
                "9538cecc-5f95-e211-a939-e4115bead28a",
                "9e38cecc-5f95-e211-a939-e4115bead28a"
            ]""",
            [
                "9538cecc-5f95-e211-a939-e4115bead28a",
                "9e38cecc-5f95-e211-a939-e4115bead28a",
            ],
        )

    def test_valid_form_no_sectors(self):
        self.check_for_valid_form(
            UserEditSectorsForm,
            """[]""",
            [],
        )

    def test_valid_form_barrier_locations(self):
        self.check_for_valid_form(
            UserEditBarrierLocationsForm,
            """[
                "TB00017",
                "9c5f66a0-5d95-e211-a939-e4115bead28a"
            ]""",
            ["TB00017", "9c5f66a0-5d95-e211-a939-e4115bead28a"],
        )

    def test_valid_form_no_barrier_locations(self):
        self.check_for_valid_form(
            UserEditBarrierLocationsForm,
            """[]""",
            [],
        )

    def test_valid_form_departments(self):
        form = UserEditGovernmentDepartmentForm(
            select_options=[
                ("1", "Test department"),
                ("2", "Test department 2"),
                ("3", "Test department 3"),
            ],
            data={"form": "1"},
        )
        assert form.is_valid()
        assert form.cleaned_data["form"] == [1]

    def test_valid_form_no_departments(self):
        form = UserEditGovernmentDepartmentForm(
            select_options=[
                ("1", "Test department"),
                ("2", "Test department 2"),
                ("3", "Test department 3"),
            ],
            data={"form": ""},
        )

        assert form.is_valid()
        assert form.cleaned_data["form"] == []
