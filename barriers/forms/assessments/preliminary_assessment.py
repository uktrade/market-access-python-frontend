from django import forms

from barriers.constants import (
    PRELIMINARY_ASSESSMENT_CHOICES,
)
from utils.api.client import MarketAccessAPIClient

from .mixins import APIFormMixin


class UpdatePreliminaryAssessmentForm(APIFormMixin, forms.Form):
    preliminary_value = forms.ChoiceField(
        label="Barrier value",
        choices=PRELIMINARY_ASSESSMENT_CHOICES,
        widget=forms.RadioSelect,
        error_messages={
            "required": "Select a value",
        },
    )

    preliminary_value_details = forms.CharField(
        widget=forms.Textarea,
        label="Provide an explanation on how the value has been assessed",
        error_messages={"required": "Enter details of the preliminary value"},
    )

    def __init__(self, preliminary_assessment=None, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier = kwargs.pop("barrier")
        self.preliminary_assessment = preliminary_assessment
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.preliminary_assessment:
            client.preliminary_assessment.patch_preliminary_assessment(
                barrier_id=self.barrier.id,
                value=self.cleaned_data["preliminary_value"],
                details=self.cleaned_data["preliminary_value_details"],
            )
        else:
            client.preliminary_assessment.create_preliminary_assessment(
                barrier_id=self.barrier.id,
                value=self.cleaned_data["preliminary_value"],
                details=self.cleaned_data["preliminary_value_details"],
            )
