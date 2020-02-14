from django import forms

from utils.api.client import MarketAccessAPIClient


class AddTypeForm(forms.Form):
    barrier_type = forms.ChoiceField(
        label='',
        choices=[],
        error_messages={'required': "Select a barrier type"},
    )

    def __init__(self, barrier_types, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['barrier_type'].choices = [
            (barrier_type['id'], barrier_type['title'])
            for barrier_type in barrier_types
        ]


class EditTypesForm(forms.Form):
    barrier_types = forms.MultipleChoiceField(
        label='',
        choices=[],
        widget=forms.MultipleHiddenInput(),
        required=False,
    )

    def __init__(self, barrier_id, barrier_types, *args, **kwargs):
        self.token = kwargs.pop('token')
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)
        self.fields['barrier_types'].choices = [
            (barrier_type['id'], barrier_type['title'])
            for barrier_type in barrier_types
        ]

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.barrier_id,
            barrier_types=self.cleaned_data['barrier_types'],
        )
