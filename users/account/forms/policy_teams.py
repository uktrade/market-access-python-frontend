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
