import json

from django import forms


class UserEditPolicyTeamsForm(forms.Form):
    form = forms.CharField(
        required=False,
    )
    label = "Policy teams"
    help_text = "Help text"
    area_variable = "policy_team"
    select_text = "Select a policy team"
    add_text = "Add team"

    def __init__(self, user_id, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.user_id = user_id
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_policy_teams = []
        if cleaned_data["form"]:
            cleaned_policy_teams = json.loads(cleaned_data["form"])
        cleaned_data["form"] = cleaned_policy_teams


class UserEditSectorsForm(forms.Form):
    form = forms.CharField(
        required=False,
    )
    label = "Sectors"
    help_text = "Help text"
    area_variable = "sector"
    select_text = "Select a sector"
    add_text = "Add sector"

    def __init__(self, user_id, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.user_id = user_id
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_sectors = []
        if cleaned_data["form"]:
            cleaned_sectors = json.loads(cleaned_data["form"])
        cleaned_data["form"] = cleaned_sectors


class UserEditBarrierLocationsForm(forms.Form):
    form = forms.CharField(
        required=False,
    )
    label = "Barrier locations"
    help_text = "All the barrier locations you're interested in by selecting them from the dropdown list. "
    "Or type the first few letters of the location name into the box."
    area_variable = "barrier_location"
    select_text = "Select a barrier location"
    add_text = "Add location"

    def __init__(self, user_id, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.user_id = user_id
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_sectors = []
        if cleaned_data["form"]:
            cleaned_sectors = json.loads(cleaned_data["form"])
        cleaned_data["form"] = cleaned_sectors


class UserEditOverseasRegionsForm(forms.Form):
    form = forms.CharField(
        required=False,
    )
    label = "Overseas regions"
    help_text = "Help text"
    area_variable = "overseas_region"
    select_text = "Select an overseas region"
    add_text = "Add region"

    def __init__(self, user_id, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.user_id = user_id
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_overseas_regions = []
        if cleaned_data["form"]:
            cleaned_overseas_regions = json.loads(cleaned_data["form"])
        cleaned_data["form"] = cleaned_overseas_regions


class UserEditGovernmentDepartmentsForm(forms.Form):
    government_departments = forms.ChoiceField(
        label="",
        choices=[],
    )

    label = "Government departments"
    help_text = "Help text"

    def __init__(self, user_id, token, government_departments, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["government_departments"].choices = government_departments

    def clean(self):
        cleaned_data = super().clean()
        cleaned_government_departments = []
        if cleaned_data["government_departments"]:
            cleaned_government_departments = json.loads(
                cleaned_data["government_departments"]
            )
        cleaned_data["government_departments"] = cleaned_government_departments
