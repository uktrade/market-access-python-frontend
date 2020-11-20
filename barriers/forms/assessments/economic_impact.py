from django import forms

from .base import ArchiveAssessmentBaseForm

from utils.api.client import MarketAccessAPIClient


class EconomicImpactAssessmentForm(forms.Form):
    impact = forms.ChoiceField(
        label="What is the economic impact of this barrier?",
        choices=[],
        error_messages={"required": "Select the economic impact of this barrier"},
    )
    explanation = forms.CharField(
        label="Explain the assessment",
        help_text=(
            "If the assessment does not cover a 5 year period - please indicate the "
            "time frame used for this assessment"
        ),
        widget=forms.Textarea,
        required=True,
        error_messages={"required": "Enter an explanation"},
    )

    def __init__(self, impacts, economic_assessment=None, economic_impact_assessment=None, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.economic_assessment = economic_assessment
        self.economic_impact_assessment = economic_impact_assessment
        super().__init__(*args, **kwargs)
        self.fields["impact"].choices = [
            (key, value)
            for key, value in impacts.items()
        ]

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.economic_impact_assessment:
            client.economic_impact_assessments.patch(
                id=self.economic_impact_assessment.id,
                **self.cleaned_data,
            )
        elif self.economic_assessment:
            client.economic_impact_assessments.create(
                economic_assessment_id=self.economic_assessment.id,
                **self.cleaned_data,
            )


class ArchiveEconomicImpactAssessmentForm(ArchiveAssessmentBaseForm):
    def archive_assessment(self):
        client = MarketAccessAPIClient(self.token)
        client.economic_impact_assessments.patch(
            id=self.id,
            archived=True,
            archived_reason=self.cleaned_data.get("archived_reason"),
        )
