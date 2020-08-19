from django import forms

from utils.api.client import MarketAccessAPIClient


class EditLocationForm(forms.Form):
    country = forms.ChoiceField(
        label="Exports to which country are affected by this issue?",
        choices=[],
        widget=forms.HiddenInput(),
    )
    admin_areas = forms.MultipleChoiceField(
        label="Exports to which country are affected by this issue?",
        choices=[],
        widget=forms.MultipleHiddenInput(),
        required=False,
    )

    def __init__(self, barrier_id, countries, admin_areas, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)
        self.fields["country"].choices = countries
        self.fields["admin_areas"].choices = admin_areas

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.barrier_id,
            country=self.cleaned_data["country"],
            admin_areas=self.cleaned_data["admin_areas"],
        )


class EditCountryOrTradingBlocForm(forms.Form):
    location = forms.ChoiceField(
        label="Which location is affected by this issue?",
        choices=[],
        error_messages={"required": "Select a location for this barrier"},
    )

    def __init__(self, countries, trading_blocs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trading_blocs = trading_blocs
        self.fields["location"].choices = (
            (
                "Trading blocs",
                tuple([(bloc["code"], bloc["name"]) for bloc in trading_blocs]),
            ),
            (
                "Countries",
                tuple((country["id"], country["name"]) for country in countries),
            ),
        )

    def clean_location(self):
        location = self.cleaned_data["location"]
        trading_bloc_codes = [trading_bloc["code"] for trading_bloc in self.trading_blocs]
        if location in trading_bloc_codes:
            self.cleaned_data["country"] = None
            self.cleaned_data["trading_bloc"] = location
        else:
            self.cleaned_data["country"] = location
            self.cleaned_data["trading_bloc"] = None


class AddAdminAreaForm(forms.Form):
    admin_area = forms.ChoiceField(
        label="Choose the parts of the country that are affected",
        choices=[],
        error_messages={"required": "Select a admin area affected by the barrier"},
    )

    def __init__(self, admin_areas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["admin_area"].choices = admin_areas
