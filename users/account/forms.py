import json

from django import forms


class UserEditPolicyTeamsForm(forms.Form):
    form = forms.CharField(
        required=False,
    )
    label = "Policy teams"
    help_text = "Help text"
    area_variable = "policy_team"
    area_text = "policy team"

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
    area_text = "sector"

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
    label = "Sectors"
    help_text = "Help text"
    area_variable = "sector"
    area_text = "sectors"

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
    area_text = "overseas region"

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
    form = forms.CharField(
        required=False,
    )
    label = "Sectors"
    help_text = "Help text"
    area_variable = "sector"
    area_text = "sectors"

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
