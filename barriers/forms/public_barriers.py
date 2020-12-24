from django import forms
from django.http import QueryDict

from .mixins import APIFormMixin

from utils.api.client import MarketAccessAPIClient
from utils.forms import YesNoBooleanField


class PublicEligibilityForm(APIFormMixin, forms.Form):
    public_eligibility = YesNoBooleanField(
        label="Does this barrier meet the criteria to be made public?",
        choices=(
            ("yes", "Allowed, it can be viewed by the public"),
            ("no", "Not allowed"),
        ),
        error_messages={"required": "Enter yes or no"},
    )
    allowed_summary = forms.CharField(
        label="Why is it allowed to be public? (optional)",
        widget=forms.Textarea,
        max_length=250,
        required=False,
        error_messages={
            "max_length": "Public eligibility summary should be %(limit_value)d characters or fewer",
        },
    )
    not_allowed_summary = forms.CharField(
        label="Why is it not allowed to be public? (optional)",
        widget=forms.Textarea,
        max_length=250,
        required=False,
        error_messages={
            "max_length": "Public eligibility summary should be %(limit_value)d characters or fewer",
        },
    )

    def get_summary(self):
        if self.cleaned_data.get("public_eligibility") is True:
            return self.cleaned_data.get("allowed_summary")
        elif self.cleaned_data.get("public_eligibility") is False:
            return self.cleaned_data.get("not_allowed_summary")
        return ""

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            public_eligibility=self.cleaned_data.get("public_eligibility"),
            public_eligibility_summary=self.get_summary(),
        )


class PublishTitleForm(APIFormMixin, forms.Form):
    title = forms.CharField(
        label="Title",
        max_length=255,
        error_messages={
            "max_length": "Title should be %(limit_value)d characters or fewer",
            "required": "Enter a title",
        },
        help_text=(
            "<a href='https://data-services-help.trade.gov.uk/market-access/how-guides/"
            "how-prepare-market-access-barrier-report-public-view/' target='_blank'>"
            "How to write a title for public view"
            "</a>"
        ),
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.public_barriers.patch(
            id=self.id,
            title=self.cleaned_data.get("title"),
        )


class PublishSummaryForm(APIFormMixin, forms.Form):
    summary = forms.CharField(
        label="Summary",
        widget=forms.Textarea,
        max_length=1500,
        error_messages={
            "max_length": "Summary should be %(limit_value)d characters or fewer",
            "required": "Enter a summary",
        },
        help_text=(
            "<a href='https://data-services-help.trade.gov.uk/market-access/how-guides/"
            "how-prepare-market-access-barrier-report-public-view/' target='_blank'>"
            "How to write a summary for public view"
            "</a>"
        ),
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.public_barriers.patch(
            id=self.id,
            summary=self.cleaned_data.get("summary"),
        )


class PublicBarrierSearchForm(forms.Form):
    organisation = forms.MultipleChoiceField(
        label="Government organisations", required=False,
    )

    def __init__(self, metadata, *args, **kwargs):
        self.metadata = metadata

        if isinstance(kwargs["data"], QueryDict):
            kwargs["data"] = self.get_data_from_querydict(kwargs["data"])

        super().__init__(*args, **kwargs)
        self.set_organisation_choices()

    def set_organisation_choices(self):
        self.fields["organisation"].choices = self.metadata.get_gov_organisation_choices()

    def get_data_from_querydict(self, data):
        """
        Get form data from the GET parameters.
        """
        cleaned_data = {
            "organisation": data.getlist("organisation"),
        }
        return {k: v for k, v in cleaned_data.items() if v}
