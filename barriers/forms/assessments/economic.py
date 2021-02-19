from django import forms
from django.conf import settings

from utils.api.client import MarketAccessAPIClient
from utils.forms import MultipleValueField, RestrictedFileField

from ..mixins import DocumentMixin
from .base import ArchiveAssessmentBaseForm


class TradeCategoryForm(forms.Form):
    trade_category = forms.ChoiceField(
        label="What is the trade category?",
        choices=[],
        error_messages={"required": "Select the trade category"},
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


class EconomicAssessmentRatingForm(DocumentMixin, forms.Form):
    rating = forms.ChoiceField(
        label="What is the initial economic assessment of this barrier?",
        choices=[],
        error_messages={"required": "Select the initial economic assessment of this barrier"},
    )
    explanation = forms.CharField(
        label="Explain the assessment",
        widget=forms.Textarea,
        required=True,
        error_messages={"required": "Enter an explanation"},
    )
    document_ids = MultipleValueField(required=False)
    document = RestrictedFileField(
        content_types=settings.ALLOWED_FILE_TYPES,
        max_upload_size=settings.FILE_MAX_SIZE,
        required=False,
    )
    ready_for_approval = forms.NullBooleanField()
    approved = forms.NullBooleanField()

    def __init__(self, ratings, barrier=None, economic_assessment=None, *args, **kwargs):
        self.barrier = barrier
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
        cleaned_data["documents"] = self.cleaned_data.pop("document_ids", [])
        del cleaned_data["document"]

    def clean_document(self):
        return self.validate_document()

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.economic_assessment:
            client.economic_assessments.patch(id=self.economic_assessment.id, **self.cleaned_data)
        elif self.barrier:
            client.economic_assessments.create(
                barrier_id=self.barrier.id,
                **self.cleaned_data,
            )


class EconomicAssessmentDocumentForm(DocumentMixin, forms.Form):
    document = RestrictedFileField(
        content_types=settings.ALLOWED_FILE_TYPES,
        max_upload_size=settings.FILE_MAX_SIZE,
    )

    def save(self):
        return self.upload_document()


class ArchiveEconomicAssessmentForm(ArchiveAssessmentBaseForm):
    def archive_assessment(self):
        client = MarketAccessAPIClient(self.token)
        client.economic_assessments.patch(
            id=self.id,
            archived=True,
            archived_reason=self.cleaned_data.get("archived_reason"),
        )
