from django import forms
from django.conf import settings

from .mixins import DocumentMixin

from utils.api.client import MarketAccessAPIClient
from utils.forms import MultipleValueField, RestrictedFileField


class EconomicAssessmentForm(DocumentMixin, forms.Form):
    IMPACT_CHOICES = (
        ('HIGH', 'High'),
        ('MEDIUMHIGH', 'Medium High'),
        ('MEDIUMLOW', 'Medium Low'),
        ('LOW', 'Low '),
    )
    impact = forms.ChoiceField(
        choices=IMPACT_CHOICES,
        widget=forms.RadioSelect,
    )
    description = forms.CharField(
        label='Explain the assessment',
        widget=forms.Textarea,
    )
    document_ids = MultipleValueField(required=False)
    document = RestrictedFileField(
        content_types=['text/csv', 'image/jpeg'],
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
            client.barriers.update_assessment(
                barrier_id=self.barrier.id,
                impact=self.cleaned_data.get('impact'),
                explanation=self.cleaned_data.get('description'),
                documents=self.cleaned_data.get('document_ids'),
            )
        else:
            client.barriers.create_assessment(
                barrier_id=self.barrier.id,
                impact=self.cleaned_data.get('impact'),
                explanation=self.cleaned_data.get('description'),
                documents=self.cleaned_data.get('document_ids'),
            )


class AssessmentDocumentForm(DocumentMixin, forms.Form):
    document = RestrictedFileField(
        content_types=['text/csv', 'image/jpeg'],
        max_upload_size=settings.FILE_MAX_SIZE,
    )

    def save(self):
        return self.upload_document()


class EconomyValueForm(forms.Form):
    value = forms.IntegerField(
        label="What is the total value of the barrier to the UK economy?",
        help_text=(
            "The estimated value of resolving the barrier to the UK economy "
            "in GBP per year."
        ),
    )

    def __init__(self, barrier, *args, **kwargs):
        self.token = kwargs.pop('token')
        self.barrier = barrier
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.barrier.has_assessment:
            client.barriers.update_assessment(
                barrier_id=self.barrier.id,
                value_to_economy=self.cleaned_data.get('value'),
            )
        else:
            client.barriers.create_assessment(
                barrier_id=self.barrier.id,
                value_to_economy=self.cleaned_data.get('value'),
            )


class MarketSizeForm(forms.Form):
    value = forms.IntegerField(
        label="What is the size of the import market?",
        help_text=(
            "The size of the import market that this barrier is limiting "
            "UK access to in GBP per year."
        ),
    )

    def __init__(self, barrier, *args, **kwargs):
        self.token = kwargs.pop('token')
        self.barrier = barrier
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.barrier.has_assessment:
            client.barriers.update_assessment(
                barrier_id=self.barrier.id,
                import_market_size=self.cleaned_data.get('value'),
            )
        else:
            client.barriers.create_assessment(
                barrier_id=self.barrier.id,
                import_market_size=self.cleaned_data.get('value'),
            )


class CommercialValueForm(forms.Form):
    value = forms.IntegerField(
        label="What is the value of the barrier to the affected business(es)?",
        help_text=(
            "The value of the barrier to the affected business(es) in GBP "
            "per year."
        ),
    )

    def __init__(self, barrier, *args, **kwargs):
        self.token = kwargs.pop('token')
        self.barrier = barrier
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.barrier.has_assessment:
            client.barriers.update_assessment(
                barrier_id=self.barrier.id,
                commercial_value=self.cleaned_data.get('value'),
            )
        else:
            client.barriers.create_assessment(
                barrier_id=self.barrier.id,
                commercial_value=self.cleaned_data.get('value'),
            )


class ExportValueForm(forms.Form):
    value = forms.IntegerField(
        label="What is the value of currently affected UK exports?",
        help_text=(
            "The value of UK exports to the partner country that are affected "
            "by this barrier in GBP per year."
        ),
    )

    def __init__(self, barrier, *args, **kwargs):
        self.token = kwargs.pop('token')
        self.barrier = barrier
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.barrier.has_assessment:
            client.barriers.update_assessment(
                barrier_id=self.barrier.id,
                export_value=self.cleaned_data.get('value'),
            )
        else:
            client.barriers.create_assessment(
                barrier_id=self.barrier.id,
                export_value=self.cleaned_data.get('value'),
            )
