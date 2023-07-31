from django import forms

from utils.api.client import MarketAccessAPIClient

EXPORT_TYPES = (
    ("goods", "Goods"),
    ("services", "Services"),
    ("investments", "Investments"),
)


class EditExportTypesForm(forms.Form):
    export_types = forms.MultipleChoiceField(
        label="",
        choices=[],
        widget=forms.MultipleHiddenInput(),
        required=False,
    )

    def __init__(self, barrier_id, export_types, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)
        self.fields["export_types"].choices = export_types

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.barrier_id, export_types=self.cleaned_data["export_types"]
        )
