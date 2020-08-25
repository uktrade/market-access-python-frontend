from django import forms

from utils.forms import YesNoDontKnowBooleanField


class NewReportBarrierLocationForm(forms.Form):
    """Form to capture Barrier Location"""
    location = forms.ChoiceField(
        label="Which location has introduced or implemented the barrier?",
        choices=[],
        widget=forms.HiddenInput(),
        error_messages={'required': "Select a location for this barrier"},
        help_text=(
            "A trading bloc should be selected if the barrier applies to the whole "
            "trading bloc. Select a country if the barrier is a national "
            "implementation of a trading bloc regulation (so only applies to that "
            "country)"
        )
    )

    def __init__(self, countries, trading_blocs, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.trading_blocs = trading_blocs
        self.fields['location'].choices = (
            ("", "Choose a location"),
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


class HasAdminAreas:
    # TODO: perhaps reword "HasAdminAreas" to "AffectsEntireCountry"
    #   as it is rather strange to read this in statements
    YES = "1"
    NO = "2"

    @classmethod
    def choices(cls):
        return (
            (cls.YES, "Yes"),
            (cls.NO, "No - just part of the country"),
        )


class NewReportBarrierLocationHasAdminAreasForm(forms.Form):
    has_admin_areas = forms.ChoiceField(
        label="Does it affect the entire country?",
        choices=HasAdminAreas.choices(),
        error_messages={'required': "Does it affect the entire country?"},
    )


class NewReportBarrierLocationAddAdminAreasForm(forms.Form):
    admin_areas = forms.ChoiceField(
        label="Which admin area is affected by the barrier?",
        choices=[],
        error_messages={
            'required': "Select an admin area affected by the barrier"
        },
    )

    def __init__(self, admin_areas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['admin_areas'].choices = admin_areas


class NewReportBarrierLocationAdminAreasForm(forms.Form):
    """
    This form can be submitted empty.
    The admin_areas.choices is considered admin areas selection which is to be used
    during create_barrier.
    """
    admin_areas = forms.ChoiceField(
        label="Selected admin areas",
        choices=[],
        required=False,
    )

    def __init__(self, admin_areas, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['admin_areas'].choices = admin_areas


class NewReportBarrierTradeDirectionForm(forms.Form):
    trade_direction = forms.ChoiceField(
        label="Which trade direction does this barrier affect?",
        choices=(),
        widget=forms.RadioSelect,
        error_messages={"required": "Select a trade direction"},
    )

    def __init__(self, trade_direction_choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["trade_direction"].choices = trade_direction_choices


class NewReportCausedByTradingBlocForm(forms.Form):
    caused_by_trading_bloc = YesNoDontKnowBooleanField(
        label="",
        error_messages={
            "required": (
                "Indicate if the barrier was caused by the trading bloc"
            )
        },
    )

    def __init__(self, trading_bloc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["caused_by_trading_bloc"].label = (
            f"Was this barrier caused by a regulation introduced by "
            f"{trading_bloc['short_name']}?"
        )
        self.fields["caused_by_trading_bloc"].help_text = (
            self.get_help_text(trading_bloc.get("code"))
        )

    def get_help_text(self, trading_bloc_code):
        help_text = {
            "TB00016": (
                "Yes should be selected if the barrier is a local application of an EU "
                "regulation. If it is an EU-wide barrier, the country location should "
                "be changed to EU in the location screen."
            )
        }
        return help_text.get(trading_bloc_code, "")
