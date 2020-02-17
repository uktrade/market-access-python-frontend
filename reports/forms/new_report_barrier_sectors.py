from django import forms


class SectorsAffected:
    YES = "1"
    NO = "0"

    @classmethod
    def choices(cls):
        return (
            (cls.YES, "Yes"),
            (cls.NO, "No, I don't know at the moment"),
        )


class NewReportBarrierHasSectorsForm(forms.Form):
    sectors_affected = forms.ChoiceField(
        label="Do you know the sector or sectors affected by the barrier?",
        choices=SectorsAffected.choices(),
        error_messages={
            'required': (
                "Select if you are aware of a sector affected by the barrier"
            )
        },
    )


class NewReportBarrierSectorsForm(forms.Form):
    sectors = forms.ChoiceField(
        label="Selected sectors",
        choices=(),
        required=False
    )

    def __init__(self, sectors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sectors'].choices = sectors


class NewReportBarrierAddSectorsForm(forms.Form):
    sectors = forms.ChoiceField(
        label="Which sector is affected by the barrier?",
        choices=(),
        error_messages={'required': "Select a sector affected by the barrier"},
    )

    def __init__(self, sectors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sectors'].choices = sectors
