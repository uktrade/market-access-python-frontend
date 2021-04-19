from django import forms
from django.http import QueryDict

from barriers.constants import PUBLIC_BARRIER_STATUSES
from utils.api.client import MarketAccessAPIClient
from utils.metadata import Metadata

from .mixins import APIFormMixin


class PublicEligibilityForm(APIFormMixin, forms.Form):
    public_eligibility = forms.ChoiceField(
        label="Does this barrier meet the criteria to be made public?",
        choices=(
            ("yes", "Allowed, it can be viewed by the public"),
            ("no", "Not allowed"),
            ("review_later", "Review later"),
        ),
        error_messages={"required": "Enter yes, no or review later"},
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
    review_later_summary = forms.CharField(
        label="Why should this barrier be reviewed at a later date?",
        widget=forms.Textarea,
        max_length=250,
        required=False,
        error_messages={
            "max_length": "Public eligibility summary should be %(limit_value)d characters or fewer",
        },
    )

    def get_summary(self):
        if self.cleaned_data.get("public_eligibility") == "no":
            return self.cleaned_data.get("not_allowed_summary")
        elif self.cleaned_data.get("public_eligibility") == "review_later":
            return self.cleaned_data.get("review_later_summary")
        return ""

    def clean(self):
        data = self.cleaned_data
        public_eligibility = data.get("public_eligibility", None)
        if public_eligibility == "no" and not data.get("not_allowed_summary"):
            raise forms.ValidationError(
                "Summary required if public view status is not allowed"
            )
        if public_eligibility == "review_later" and not data.get(
            "review_later_summary"
        ):
            raise forms.ValidationError(
                "Summary required if public view status is be reviewed later"
            )
        return data

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.cleaned_data.get("public_eligibility") == "review_later":
            client.barriers.patch(
                id=self.id,
                public_eligibility_postponed=True,
                public_eligibility=False,
                public_eligibility_summary=self.get_summary(),
            )
        else:
            client.barriers.patch(
                id=self.id,
                public_eligibility=self.cleaned_data.get("public_eligibility"),
                public_eligibility_postponed=False,
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
    region = forms.MultipleChoiceField(label="Overseas Regions", required=False)
    organisation = forms.MultipleChoiceField(
        label="Government organisations",
        required=False,
    )
    sector = forms.MultipleChoiceField(
        label="Sector",
        required=False,
    )
    country = forms.MultipleChoiceField(label="Country", required=False)
    status = forms.MultipleChoiceField(
        label="Status", required=False, initial=["20", "30"]
    )

    def __init__(self, metadata: Metadata, *args, **kwargs):
        self.metadata = metadata

        if isinstance(kwargs["data"], QueryDict):
            kwargs["data"] = self.get_data_from_querydict(kwargs["data"])

        super().__init__(*args, **kwargs)
        self.set_organisation_choices()
        self.set_sector_choices()
        self.set_country_choices()
        self.set_status_choices()
        self.set_region_choices()

    def set_organisation_choices(self):
        self.fields[
            "organisation"
        ].choices = self.metadata.get_gov_organisation_choices()

    def set_sector_choices(self):
        self.fields["sector"].choices = self.metadata.get_sector_choices(level=0)

    def set_country_choices(self):
        self.fields["country"].choices = self.metadata.get_country_choices()

    def set_status_choices(self):
        self.fields["status"].choices = PUBLIC_BARRIER_STATUSES + (
            ("changed", "Barriers changed internally since being made public"),
        )

    def set_region_choices(self):
        self.fields["region"].choices = self.metadata.get_overseas_region_choices()

    def get_data_from_querydict(self, data):
        """
        Get form data from the GET parameters.
        """

        cleaned_data = {
            "organisation": data.getlist("organisation"),
            "sector": data.getlist("sector"),
            "country": data.getlist("country"),
            "status": data.getlist("status", ["20", "30"]),
            "region": data.getlist("region"),
        }
        return {k: v for k, v in cleaned_data.items() if v}
