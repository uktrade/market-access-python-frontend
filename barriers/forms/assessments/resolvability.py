from django import forms
from django.template.loader import render_to_string

from .base import ArchiveAssessmentBaseForm

from utils.api.client import MarketAccessAPIClient


class ResolvabilityAssessmentForm(forms.Form):
    time_to_resolve = forms.ChoiceField(
        label="How much time would it take to resolve this barrier?",
        choices=[],
        error_messages={"required": "Select how much time it would take to resolve this barrier"},
        help_text=render_to_string("barriers/assessments/resolvability/help_text/time_to_resolve.html")
    )
    effort_to_resolve = forms.ChoiceField(
        label="How much effort will it take to resolve this barrier?",
        choices=[],
        error_messages={"required": "Select how much effort it would take to resolve this barrier"},
        help_text=render_to_string("barriers/assessments/resolvability/help_text/effort_to_resolve.html")
    )
    explanation = forms.CharField(
        label="Explain the assessment",
        help_text="Please explain why you have given the above ratings.",
        widget=forms.Textarea,
        max_length=500,
        required=True,
        error_messages={
            "max_length": "Explanation should be %(limit_value)d characters or fewer",
            "required": "Enter an explanation",
        },
    )
    approved = forms.NullBooleanField()

    def __init__(
        self,
        time_to_resolve,
        effort_to_resolve,
        barrier=None,
        resolvability_assessment=None,
        *args,
        **kwargs,
    ):
        self.token = kwargs.pop("token")
        self.barrier = barrier
        self.resolvability_assessment = resolvability_assessment
        super().__init__(*args, **kwargs)
        self.fields["time_to_resolve"].choices = [
            (key, value)
            for key, value in time_to_resolve.items()
        ]
        self.fields["effort_to_resolve"].choices = [
            (key, value)
            for key, value in effort_to_resolve.items()
        ]

    def clean(self):
        cleaned_data = super().clean()
        if self.cleaned_data["approved"] is None:
            del cleaned_data["approved"]

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.resolvability_assessment:
            client.resolvability_assessments.patch(id=self.resolvability_assessment.id, **self.cleaned_data)
        elif self.barrier:
            client.resolvability_assessments.create(barrier_id=self.barrier.id, **self.cleaned_data)


class ArchiveResolvabilityAssessmentForm(ArchiveAssessmentBaseForm):
    def archive_assessment(self):
        client = MarketAccessAPIClient(self.token)
        client.resolvability_assessments.patch(
            id=self.id,
            archived=True,
            archived_reason=self.cleaned_data.get("archived_reason"),
        )
