from django import forms

from utils.api.client import MarketAccessAPIClient

from .base import ArchiveAssessmentBaseForm


class EconomicImpactAssessmentForm(forms.Form):
    impact = forms.ChoiceField(
        label="What is the valuation of this barrier?",
        choices=[],
        error_messages={"required": "Select the valuation of this barrier"},
    )
    explanation = forms.CharField(
        label="Explain the assessment",
        widget=forms.Textarea,
        required=True,
        error_messages={"required": "Enter an explanation"},
    )

    def __init__(
        self,
        impacts,
        economic_assessment=None,
        economic_impact_assessment=None,
        *args,
        **kwargs
    ):
        self.token = kwargs.pop("token")
        self.economic_assessment = economic_assessment
        self.economic_impact_assessment = economic_impact_assessment
        super().__init__(*args, **kwargs)
        self.fields["impact"].choices = [(key, value) for key, value in impacts.items()]

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
                barrier_id=self.barrier.id,
                **self.cleaned_data,
            )
        else:
            # case where a barrier has no pre-existing economic assessment
            client.economic_impact_assessments.create(
                barrier_id=self.barrier.id,
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
