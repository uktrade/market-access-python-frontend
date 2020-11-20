from django import forms

from .base import ArchiveAssessmentBaseForm

from utils.api.client import MarketAccessAPIClient


class StrategicAssessmentForm(forms.Form):
    hmg_strategy = forms.CharField(
        label=(
            "Is the barrier aligned with wider HMG strategic objectives (such as the "
            "Industrial Strategy, Levelling Up agenda, Export Strategy)?"
        ),
        widget=forms.Textarea,
        max_length=500,
        required=True,
        error_messages={
            "max_length": "HMG strategic objectives should be %(limit_value)d characters or fewer",
            "required": "Enter HMG strategic objectives",
        },
    )
    government_policy = forms.CharField(
        label=(
            "Is the barrier aligned with wider government policies (such as free trade "
            "principles, climate change, anti-corruption or tax avoidance agreements)?"
        ),
        widget=forms.Textarea,
        max_length=500,
        required=True,
        error_messages={
            "max_length": "Wider government policies should be %(limit_value)d characters or fewer",
            "required": "Enter wider government policies",
        },
    )
    trading_relations = forms.CharField(
        label=(
            "Does resolving the barrier strategically improve trading relations within "
            "other countries (such as FTA countries, future FTA/growth countries)?"
        ),
        widget=forms.Textarea,
        max_length=500,
        required=True,
        error_messages={
            "max_length": "Strategic improvement to trading relations should be %(limit_value)d characters or fewer",
            "required": "Enter strategic improvement to trading relations",
        },
    )
    uk_interest_and_security = forms.CharField(
        label=(
            "Does resolving the barrier affect UK interest and / or national security?"
        ),
        widget=forms.Textarea,
        max_length=500,
        required=True,
        error_messages={
            "max_length": "UK interests or national security should be %(limit_value)d characters or fewer",
            "required": "Enter UK interests or national security",
        },
    )
    uk_grants = forms.CharField(
        label=(
            "Is the barrier connected with UK grants (such as Prosperity Fund, Market "
            "Access fund) and supports International Development Objectives ODA?"
        ),

        widget=forms.Textarea,
        max_length=500,
        required=True,
        error_messages={
            "max_length": "UK grants should be %(limit_value)d characters or fewer",
            "required": "Enter UK grants",
        },
    )
    competition = forms.CharField(
        label=(
            "In what way does competition and other in-country policies affect this barrier?"
        ),
        widget=forms.Textarea,
        max_length=500,
        required=True,
        error_messages={
            "max_length": "Competition or in-country policies should be %(limit_value)d characters or fewer",
            "required": "Enter competition or in-country policies",
        },
    )
    additional_information = forms.CharField(
        label=(
            "Additional information not captured above"
        ),
        widget=forms.Textarea,
        max_length=500,
        required=False,
        error_messages={
            "max_length": "Explanation should be %(limit_value)d characters or fewer",
            "required": "Enter an explanation",
        },
    )
    scale = forms.ChoiceField(
        label="Strategic assessment scale",
        choices=[],
        error_messages={"required": "Select a strategic assessment value"},
    )
    approved = forms.NullBooleanField()

    def __init__(self, scale, barrier=None, strategic_assessment=None, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier = barrier
        self.strategic_assessment = strategic_assessment
        super().__init__(*args, **kwargs)
        self.fields["scale"].choices = [
            (key, value)
            for key, value in scale.items()
        ]

    def clean(self):
        cleaned_data = super().clean()
        if self.cleaned_data["approved"] is None:
            del cleaned_data["approved"]

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.strategic_assessment:
            client.strategic_assessments.patch(id=self.strategic_assessment.id, **self.cleaned_data)
        elif self.barrier:
            client.strategic_assessments.create(barrier_id=self.barrier.id, **self.cleaned_data)


class ArchiveStrategicAssessmentForm(ArchiveAssessmentBaseForm):
    def archive_assessment(self):
        client = MarketAccessAPIClient(self.token)
        client.strategic_assessments.patch(
            id=self.id,
            archived=True,
            archived_reason=self.cleaned_data.get("archived_reason"),
        )
