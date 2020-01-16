from django import forms

from .mixins import CustomErrorsMixin

from utils.api_client import MarketAccessAPIClient


class EditSectorsForm(forms.Form):
    sectors = forms.MultipleChoiceField(
        label='',
        choices=[],
        widget=forms.MultipleHiddenInput(),
        required=False,
    )
    all_sectors = forms.BooleanField(
        widget=forms.HiddenInput(),
        required=False,
    )

    def __init__(self, barrier_id, sectors, *args, **kwargs):
        self.token = kwargs.pop('token')
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)
        self.fields['sectors'].choices = sectors

    def save(self):
        client = MarketAccessAPIClient(self.token)
        sectors_affected = False
        if (
            len(self.cleaned_data['sectors']) > 0
            or self.cleaned_data['all_sectors']
        ):
            sectors_affected = True

        client.barriers.patch(
            id=self.barrier_id,
            sectors=self.cleaned_data['sectors'],
            all_sectors=self.cleaned_data['all_sectors'],
            sectors_affected=sectors_affected,
        )


class AddSectorsForm(CustomErrorsMixin, forms.Form):
    sector = forms.ChoiceField(label='', choices=[])

    def __init__(self, sectors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sector'].choices = sectors
