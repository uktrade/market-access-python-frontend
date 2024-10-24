import json

from django import forms

from utils.api.client import MarketAccessAPIClient


class UserEditPolicyTeamsForm(forms.Form):
    policy_teams = forms.CharField(
        label="Label",
        help_text="Help text",
        required=False,
    )

    def __init__(self, user_id, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.user_id = user_id
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_policy_teams = []
        if cleaned_data["policy_teams"]:
            cleaned_policy_teams = json.loads(cleaned_data["policy_teams"])
        cleaned_data["policy_teams"] = cleaned_policy_teams
