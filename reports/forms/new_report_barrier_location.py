from django import forms

from barriers.forms.edit import CausedByTradingBlocForm
from barriers.forms.location import EditCountryOrTradingBlocForm


class NewReportBarrierLocationForm(EditCountryOrTradingBlocForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].choices = (
            [("", "Choose a location")] + self.fields['location'].choices
        )


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


class NewReportCausedByTradingBlocForm(CausedByTradingBlocForm):
    pass
