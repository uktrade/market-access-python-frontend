import logging

from django import forms

from utils.api.client import MarketAccessAPIClient

logger = logging.getLogger(__name__)


class EditLocationForm(forms.Form):
    country = forms.ChoiceField(
        choices=[],
        widget=forms.HiddenInput(),
        required=False,
    )
    trading_bloc = forms.ChoiceField(
        choices=[],
        widget=forms.HiddenInput(),
        required=False,
    )
    admin_areas = forms.MultipleChoiceField(
        choices=[],
        widget=forms.MultipleHiddenInput(),
        required=False,
    )

    def __init__(
        self, barrier_id, countries, admin_areas, trading_blocs, *args, **kwargs
    ):
        self.token = kwargs.pop("token")
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)
        self.fields["country"].choices = [
            (country["id"], country["name"]) for country in countries
        ]
        self.fields["admin_areas"].choices = [
            (admin_area["id"], admin_area["name"]) for admin_area in admin_areas
        ]
        self.fields["trading_bloc"].choices = [
            (trading_bloc["code"], trading_bloc["name"])
            for trading_bloc in trading_blocs
        ]

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.barrier_id,
            country=self.cleaned_data["country"] or None,
            admin_areas=self.cleaned_data["admin_areas"],
            trading_bloc=self.cleaned_data["trading_bloc"],
        )


class EditCountryOrTradingBlocForm(forms.Form):
    location = forms.ChoiceField(
        label="Which location is affected by this issue?",
        choices=[],
        error_messages={"required": "Select a location for this barrier"},
        help_text=(
            "A trading bloc should be selected if the barrier applies to the whole "
            "trading bloc. Select a country if the barrier is a national "
            "implementation of a trading bloc regulation (so only applies to that "
            "country)"
        ),
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
        trading_bloc_codes = [
            trading_bloc["code"] for trading_bloc in self.trading_blocs
        ]
        if location in trading_bloc_codes:
            self.cleaned_data["country"] = None
            self.cleaned_data["trading_bloc"] = location
        else:
            self.cleaned_data["country"] = location
            self.cleaned_data["trading_bloc"] = ""
        return location


class AddAdminAreaForm(forms.Form):
    admin_area = forms.ChoiceField(
        label="Choose the parts of the country that are affected",
        choices=[],
        error_messages={"required": "Select a admin area affected by the barrier"},
    )

    def __init__(self, admin_areas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["admin_area"].choices = admin_areas
