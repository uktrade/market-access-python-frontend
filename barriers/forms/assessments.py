from django import forms
from django.conf import settings

from .mixins import DocumentMixin

from utils.api.client import MarketAccessAPIClient
from utils.forms import MultipleValueField, RestrictedFileField


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
            client.barriers.update_assessment(
                barrier_id=self.barrier.id,
                impact=self.cleaned_data.get("impact"),
                explanation=self.cleaned_data.get("description"),
                documents=self.cleaned_data.get("document_ids"),
            )
        else:
            client.barriers.create_assessment(
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

    def __init__(self, barrier, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier = barrier
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.barrier.has_assessment:
            client.barriers.update_assessment(
                barrier_id=self.barrier.id,
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


class AutoAssessmentForm(forms.Form):
    product_codes = forms.CharField(
        label="Commodity codes",
        help_text="Comma separated list of product codes",
        widget=forms.Textarea,
    )
    year = forms.IntegerField(label="Year", help_text="Leave blank to use most recent available", min_value=2002, max_value=2020, required=False)
    product_title = forms.CharField(label="Product title", max_length=255)
    country1 = forms.CharField(label="Country 1", help_text="Needs to be exactly as in the Comtrade API", max_length=255)
    country1print = forms.CharField(label="Country 2 print", help_text="If different to Country 1", max_length=255, required=False)
    country2 = forms.CharField(label="Country 2", help_text="Usually United Kingdom", max_length=255)
    country2print = forms.CharField(label="Country 2 print", help_text="If different to Country 2", max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token")
        super().__init__(*args, **kwargs)

    def clean_product_codes(self):
        codes = self.cleaned_data["product_codes"]
        codes = codes.replace(";", ",")
        codes = codes.replace('"', "")
        return ",".join([
            code.strip() for code in codes.split(",")
        ]).strip(",")

    def process(self):
        client = MarketAccessAPIClient(self.token)

        return client.get(
            path="auto-assessment",
            params={
                "year": self.cleaned_data["year"],
                "product_codes": self.cleaned_data["product_codes"],
                "product_title": self.cleaned_data["product_title"],
                "country1": self.cleaned_data["country1"],
                "country1print": self.cleaned_data["country1print"],
                "country2": self.cleaned_data["country2"],
                "country2print": self.cleaned_data["country2print"],
            }
        )
