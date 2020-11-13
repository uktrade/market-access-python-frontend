from django import forms
from django.conf import settings
from django.template.loader import render_to_string

from barriers.forms.mixins import APIFormMixin
from .mixins import DocumentMixin

from utils.api.client import MarketAccessAPIClient
from utils.forms import MultipleValueField, RestrictedFileField, YesNoBooleanField


class EconomicAssessmentForm(DocumentMixin, forms.Form):
    IMPACT_CHOICES = (
        ("HIGH", "High"),
        ("MEDIUMHIGH", "Medium High"),
        ("MEDIUMLOW", "Medium Low"),
        ("LOW", "Low "),
    )
    impact = forms.ChoiceField(
        choices=IMPACT_CHOICES,
        widget=forms.RadioSelect,
        error_messages={"required": "Select an economic impact"},
    )
    description = forms.CharField(
        label="Explain the assessment",
        widget=forms.Textarea,
        error_messages={"required": "Explain the assessment"},
    )
    document_ids = MultipleValueField(required=False)
    document = RestrictedFileField(
        content_types=settings.ALLOWED_FILE_TYPES,
        max_upload_size=settings.FILE_MAX_SIZE,
        required=False,
    )

    def __init__(self, barrier, *args, **kwargs):
        self.barrier = barrier
        super().__init__(*args, **kwargs)

    def clean_document(self):
        return self.validate_document()

    def save(self):
        client = MarketAccessAPIClient(self.token)

        if self.barrier.has_assessment:
            client.economic_assessments.update(
                barrier_id=self.barrier.id,
                impact=self.cleaned_data.get("impact"),
                explanation=self.cleaned_data.get("description"),
                documents=self.cleaned_data.get("document_ids"),
            )
        else:
            client.economic_assessments.create(
                barrier_id=self.barrier.id,
                impact=self.cleaned_data.get("impact"),
                explanation=self.cleaned_data.get("description"),
                documents=self.cleaned_data.get("document_ids"),
            )


class AssessmentDocumentForm(DocumentMixin, forms.Form):
    document = RestrictedFileField(
        content_types=settings.ALLOWED_FILE_TYPES,
        max_upload_size=settings.FILE_MAX_SIZE,
    )

    def save(self):
        return self.upload_document()


class EconomyValueForm(forms.Form):
    value = forms.IntegerField(
        min_value=0,
        max_value=1000000000000,
        localize=True,
        label="What is the total value of the barrier to the UK economy?",
        help_text=(
            "The estimated value of resolving the barrier to the UK economy "
            "in GBP per year."
        ),
        error_messages={
            "required": "Enter a value",
            "min_value": "Enter a valid number",
            "max_value": "Enter a valid number",
        },
    )

    def __init__(self, barrier=None, economic_assessment_id=None, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier = barrier
        self.economic_assessment_id = economic_assessment_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.barrier.has_assessment:
            client.barriers.update_assessment(
                id=self.economic_assessment_id,
                value_to_economy=self.cleaned_data.get("value"),
            )
        else:
            client.barriers.create_assessment(
                barrier_id=self.barrier.id,
                value_to_economy=self.cleaned_data.get("value"),
            )


class MarketSizeForm(forms.Form):
    value = forms.IntegerField(
        min_value=0,
        max_value=1000000000000,
        localize=True,
        label="What is the size of the import market?",
        help_text=(
            "The size of the import market that this barrier is limiting "
            "UK access to in GBP per year."
        ),
        error_messages={
            "required": "Enter a value",
            "min_value": "Enter a valid number",
            "max_value": "Enter a valid number",
        },
    )

    def __init__(self, barrier, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier = barrier
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.barrier.has_assessment:
            client.barriers.update_assessment(
                barrier_id=self.barrier.id,
                import_market_size=self.cleaned_data.get("value"),
            )
        else:
            client.barriers.create_assessment(
                barrier_id=self.barrier.id,
                import_market_size=self.cleaned_data.get("value"),
            )


class CommercialValueForm(forms.Form):
    value = forms.IntegerField(
        min_value=0,
        max_value=1000000000000,
        localize=True,
        label="What is the value of the barrier to the affected business(es) in GBP?",
        error_messages={
            "required": "Enter a value",
            "min_value": "Enter a valid number",
            "max_value": "Enter a valid number",
        },
    )
    value_explanation = forms.CharField(
        widget=forms.Textarea,
        error_messages={"required": "Enter a value description and timescale"},
    )

    def __init__(self, barrier, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier = barrier
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        payload = {
            "commercial_value": self.cleaned_data.get("value"),
            "commercial_value_explanation": self.cleaned_data.get("value_explanation")
        }
        if self.barrier.has_assessment:
            client.barriers.update_assessment(barrier_id=self.barrier.id, **payload)
        else:
            client.barriers.create_assessment(barrier_id=self.barrier.id, **payload)


class ExportValueForm(forms.Form):
    value = forms.IntegerField(
        min_value=0,
        max_value=1000000000000,
        localize=True,
        label="What is the value of currently affected UK exports?",
        help_text=(
            "The value of UK exports to the partner country that are affected "
            "by this barrier in GBP per year."
        ),
        error_messages={
            "required": "Enter a value",
            "min_value": "Enter a valid number",
            "max_value": "Enter a valid number",
        },
    )

    def __init__(self, barrier, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier = barrier
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.barrier.has_assessment:
            client.barriers.update_assessment(
                barrier_id=self.barrier.id, export_value=self.cleaned_data.get("value"),
            )
        else:
            client.barriers.create_assessment(
                barrier_id=self.barrier.id, export_value=self.cleaned_data.get("value"),
            )


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


class ArchiveAssessmentBaseForm(APIFormMixin, forms.Form):
    are_you_sure = YesNoBooleanField(
        label="Are you sure you want to archive this assessment?",
        error_messages={"required": "Enter yes or no"},
    )
    archived_reason = forms.CharField(
        label="Why are you archiving this assessment? (optional)",
        widget=forms.Textarea,
        max_length=500,
        required=False,
    )

    def archive_assessment(self):
        raise NotImplementedError

    def save(self):
        if self.cleaned_data.get("are_you_sure") is True:
            self.archive_assessment()


class ArchiveResolvabilityAssessmentForm(ArchiveAssessmentBaseForm):
    def archive_assessment(self):
        client = MarketAccessAPIClient(self.token)
        client.resolvability_assessments.patch(
            id=self.id,
            archived=True,
            archived_reason=self.cleaned_data.get("archived_reason"),
        )


class ArchiveStrategicAssessmentForm(ArchiveAssessmentBaseForm):
    def archive_assessment(self):
        client = MarketAccessAPIClient(self.token)
        client.strategic_assessments.patch(
            id=self.id,
            archived=True,
            archived_reason=self.cleaned_data.get("archived_reason"),
        )


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
    analysis_data = forms.CharField(
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
