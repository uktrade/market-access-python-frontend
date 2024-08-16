import logging

from django import forms

from utils.api.client import MarketAccessAPIClient

logger = logging.getLogger(__name__)


class AddPolicyTeamForm(forms.Form):
    policy_team = forms.ChoiceField(
        label="",
        choices=[],
        error_messages={"required": "Select a policy team"},
    )

    def __init__(self, policy_teams, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["policy_team"].choices = [
            (policy_team["id"], policy_team["title"]) for policy_team in policy_teams
        ]


class EditPolicyTeamsForm(forms.Form):
    policy_teams = forms.MultipleChoiceField(
        label="",
        choices=[],
        widget=forms.MultipleHiddenInput(),
        required=False,
    )

    def __init__(self, barrier_id, policy_teams, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)
        self.fields["policy_teams"].choices = [
            (policy_team["id"], policy_team["title"]) for policy_team in policy_teams
        ]

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.barrier_id,
            policy_teams=self.cleaned_data["policy_teams"],
        )
