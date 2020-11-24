from django import forms

from .base import ArchiveAssessmentBaseForm

from utils.api.client import MarketAccessAPIClient


class TradeCategoryForm(forms.Form):
    trade_category = forms.ChoiceField(
        label="What is the barrier type?",
        choices=[],
        error_messages={"required": "Select the barrier type"},
    )

    def __init__(self, trade_categories, barrier=None, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier = barrier
        super().__init__(*args, **kwargs)
        self.fields["trade_category"].choices = [
            (key, value)
            for key, value in trade_categories.items()
        ]

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(id=self.barrier.id, trade_category=self.cleaned_data["trade_category"])


class AnalysisDataForm(forms.Form):
    user_analysis_data = forms.CharField(
        label="Add the initial assessment data",
        help_text="Paste in the initial assessment data in the text box below.",
        widget=forms.Textarea,
        required=True,
        error_messages={"required": "Enter the initial assessment data"},
    )

    def __init__(self, barrier=None, economic_assessment=None, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier = barrier
        self.economic_assessment = economic_assessment
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.economic_assessment:
            client.economic_assessments.patch(id=self.economic_assessment.id, **self.cleaned_data)
        elif self.barrier:
            self.economic_assessment = client.economic_assessments.create(
                barrier_id=self.barrier.id,
                **self.cleaned_data,
            )


class EconomicAssessmentRatingForm(forms.Form):
    rating = forms.ChoiceField(
        label="What is the economic rating of this barrier?",
        choices=[],
        error_messages={"required": "Select the economic rating of this barrier"},
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
    ready_for_approval = forms.NullBooleanField()
    approved = forms.NullBooleanField()

    def __init__(self, ratings, economic_assessment=None, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.economic_assessment = economic_assessment
        super().__init__(*args, **kwargs)
        self.fields["rating"].choices = [
            (key, value)
            for key, value in ratings.items()
        ]

    def clean(self):
        cleaned_data = super().clean()
        if self.cleaned_data["ready_for_approval"] is None:
            del cleaned_data["ready_for_approval"]
        if self.cleaned_data["approved"] is None:
            del cleaned_data["approved"]

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.economic_assessments.patch(id=self.economic_assessment.id, **self.cleaned_data)


class ArchiveEconomicAssessmentForm(ArchiveAssessmentBaseForm):
    def archive_assessment(self):
        client = MarketAccessAPIClient(self.token)
        client.economic_assessments.patch(
            id=self.id,
            archived=True,
            archived_reason=self.cleaned_data.get("archived_reason"),
        )
