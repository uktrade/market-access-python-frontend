from django import forms


class NewReportBarrierLocationForm(forms.Form):
    """Form to capture Barrier Location"""
    country = forms.ChoiceField(
        label="Which country has introduced the barrier?",
        choices=[],
        widget=forms.HiddenInput(),
    )

    def __init__(self, countries, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].choices = countries


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
    )


class NewReportBarrierLocationAddAdminAreasForm(forms.Form):
    admin_areas = forms.ChoiceField(
        label="Which admin area is affected by the barrier?",
        choices=[],
    )

    def __init__(self, admin_areas, *args, **kwargs):
        # self.token = kwargs.pop('token')
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
        required=False
    )

    def __init__(self, admin_areas, *args, **kwargs):
        # self.token = kwargs.pop('token')
        super().__init__(*args, **kwargs)
        self.fields['admin_areas'].choices = admin_areas
