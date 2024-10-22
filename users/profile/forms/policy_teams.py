from django import forms


class UserEditPolicyTeamsForm(forms.Form):
    policy_teams = forms.MultipleChoiceField(
        label="",
        choices=[],
        widget=forms.MultipleHiddenInput(),
        required=False,
    )
    label = "Placeholder"
    help_text = "Placeholder"
    required = False

    def __init__(self, user_id, policy_teams, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.user_id = user_id
        super().__init__(*args, **kwargs)
        self.fields["policy_teams"].choices = [
            (policy_team["id"], policy_team["title"]) for policy_team in policy_teams
        ]

    # def save(self):
    #     client = MarketAccessAPIClient(self.token)
    #     client.barriers.patch(
    #       HOW?
    #     )
