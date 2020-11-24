from django import forms

from utils.api.client import MarketAccessAPIClient


class EditGovernmentOrganisationsForm(forms.Form):
    organisations = forms.MultipleChoiceField(
        label="", choices=[], widget=forms.MultipleHiddenInput(), required=False,
    )

    def __init__(self, barrier_id, organisations, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)
        self.fields["organisations"].choices = organisations

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.barrier_id, government_organisations=self.cleaned_data["organisations"],
        )


class AddGovernmentOrganisationsForm(forms.Form):
    organisation = forms.ChoiceField(
        label="",
        choices=[],
        error_messages={
            "required": "Select an organisation that is related to the barrier"
        },
    )

    def __init__(self, organisations, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["organisation"].choices = organisations
