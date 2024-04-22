import logging

from django import forms
from django.http import QueryDict

from barriers.constants import AWAITING_REVIEW_FROM, PUBLIC_BARRIER_STATUSES
from utils.api.client import MarketAccessAPIClient
from utils.forms.fields import TrueFalseBooleanField
from utils.metadata import Metadata

from .mixins import APIFormMixin

logger = logging.getLogger(__name__)


class PublicEligibilityForm(APIFormMixin, forms.Form):

    public_eligibility = forms.ChoiceField(
        label="Should this barrier be made public on GOV.UK, once it has been approved?",
        choices=(
            ("yes", "Yes, it can be published once approved"),
            ("no", "No, it cannot be published"),
        ),
        required=False,
    )
    public_eligibility_summary = forms.CharField(
        label="Explain why the barrier should not be published",
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": 5,
            },
        ),
        required=False,
        initial="",
    )

    def clean(self):
        cleaned_data = super().clean()

        # Need to check for required field. Needs to be done here or the key
        # will be missing for the summary check later in the method.
        if (
            "public_eligibility" not in cleaned_data.keys()
            or cleaned_data["public_eligibility"] == ""
        ):
            msg = "Select whether this barrier should be published on GOV.UK, once approved"
            self.add_error("public_eligibility", msg)
            return

        # Summary required if barrier cannot be published
        if (
            cleaned_data["public_eligibility"] == "no"
            and cleaned_data["public_eligibility_summary"] == ""
        ):
            msg = "Enter a reason for not publishing this barrier"
            self.add_error("public_eligibility_summary", msg)

    def save(self):
        client = MarketAccessAPIClient(self.token)

        client.barriers.patch(
            id=self.id,
            public_eligibility=self.cleaned_data.get("public_eligibility"),
            public_eligibility_summary=self.cleaned_data.get(
                "public_eligibility_summary"
            ),
        )

        if self.cleaned_data.get("public_eligibility") == "no":
            # Clear public title and summary of the barrier in case we are changing this
            # barrier to Not Allowed from previously Allowed
            client.public_barriers.report_public_barrier_field(
                id=self.id,
                form_name="barrier-public-title",
                values={"title": ""},
            )
            client.public_barriers.report_public_barrier_field(
                id=self.id,
                form_name="barrier-public-summary",
                values={"summary": ""},
            )


class PublishTitleForm(APIFormMixin, forms.Form):
    title = forms.CharField(
        label="Public title",
        help_text=("Provide a title that is suitable for the public to read."),
        max_length=150,
        error_messages={
            "max_length": "Title should be %(limit_value)d characters or less",
            "required": "Enter a public title for this barrier",
        },
        widget=forms.Textarea(
            attrs={
                "class": "govuk-input govuk-js-character-count js-character-count",
                "rows": 10,
            },
        ),
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)

        client.public_barriers.report_public_barrier_field(
            id=self.id,
            form_name="barrier-public-title",
            values={"title": self.cleaned_data.get("title")},
        )


class PublishSummaryForm(APIFormMixin, forms.Form):
    summary = forms.CharField(
        label="Public summary",
        help_text=("Provide a summary that is suitable for the public to read."),
        max_length=1500,
        error_messages={
            "max_length": "Summary should be %(limit_value)d characters or less",
            "required": "Enter a public summary for this barrier",
        },
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea govuk-js-character-count js-character-count",
                "rows": 5,
            },
        ),
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)

        client.public_barriers.report_public_barrier_field(
            id=self.id,
            form_name="barrier-public-summary",
            values={"summary": self.cleaned_data.get("summary")},
        )


class ApprovePublicBarrierForm(APIFormMixin, forms.Form):
    content_clearance = TrueFalseBooleanField(
        required=True,
        widget=forms.CheckboxInput(
            attrs={
                "class": "govuk-checkboxes__input",
            },
        ),
    )
    external_clearances = TrueFalseBooleanField(
        required=True,
        label=("I confirm this barrier has all the necessary clearances needed"),
        widget=forms.CheckboxInput(
            attrs={
                "class": "govuk-checkboxes__input",
            },
        ),
    )
    public_approval_summary = forms.CharField(
        label="Any additional information to support your decision? (optional)",
        max_length=500,
        required=False,
        error_messages={
            "max_length": "Summary should be %(limit_value)d characters or less",
        },
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea govuk-js-character-count js-character-count",
                "aria-describedby": "id_public_approval_summary-info",
                "rows": 5,
            },
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        if "Send to GOV.UK content team" in self.data["submit_approval"]:
            if cleaned_data["content_clearance"] is False:
                msg = "Confirm if the barrier content is approved"
                self.add_error("content_clearance", msg)
            if cleaned_data["external_clearances"] is False:
                msg = "Confirm if the barrier is cleared with relevant parties"
                self.add_error("external_clearances", msg)

    def save(self):
        client = MarketAccessAPIClient(self.token)

        public_approval_summary = self.cleaned_data.get("public_approval_summary")
        if public_approval_summary != "":
            client.public_barriers.patch(
                id=self.id,
                approvers_summary=public_approval_summary,
            )

        if "Send to GOV.UK content team" in self.data["submit_approval"]:
            client.public_barriers.ready_for_publishing(id=self.id)
        else:
            # Not allowed button pressed, need to change public eligibility
            # and clear the public title and summary
            client.barriers.patch(
                id=self.id,
                public_eligibility="no",
                public_eligibility_summary=public_approval_summary,
            )
            client.public_barriers.report_public_barrier_field(
                id=self.id,
                form_name="barrier-public-title",
                values={"title": ""},
            )
            client.public_barriers.report_public_barrier_field(
                id=self.id,
                form_name="barrier-public-summary",
                values={"summary": ""},
            )


class PublishPublicBarrierForm(APIFormMixin, forms.Form):
    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.public_barriers.publish(id=self.id)


class UnpublishPublicBarrierForm(APIFormMixin, forms.Form):
    public_publisher_summary = forms.CharField(
        label="Reason for removing the barrier",
        max_length=500,
        required=False,
        error_messages={
            "max_length": "Summary should be %(limit_value)d characters or less",
        },
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea govuk-js-character-count js-character-count",
                "rows": 5,
            },
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data["public_publisher_summary"] == "":
            msg = "Provide a reason for unpublishing the barrier."
            self.add_error("public_publisher_summary", msg)

    def save(self):
        client = MarketAccessAPIClient(self.token)

        client.public_barriers.patch(
            id=self.id,
            publishers_summary=self.cleaned_data.get("public_publisher_summary"),
        )

        client.public_barriers.unpublish(id=self.id)


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
    country = forms.MultipleChoiceField(label="Location", required=False)
    status = forms.MultipleChoiceField(
        label="Status", required=False, initial=["20", "30"]
    )
    awaiting_review_from = forms.MultipleChoiceField(
        label="Awaiting review from",
        required=False,
    )

    def __init__(self, metadata: Metadata, *args, **kwargs):
        self.metadata = metadata

        if isinstance(kwargs["data"], QueryDict):
            kwargs["data"] = self.get_data_from_querydict(kwargs["data"])

        super().__init__(*args, **kwargs)
        self.set_awaiting_review_from_choices()
        self.set_organisation_choices()
        self.set_sector_choices()
        self.set_country_choices()
        self.set_status_choices()
        self.set_region_choices()

    def set_awaiting_review_from_choices(self):
        self.fields["awaiting_review_from"].choices = AWAITING_REVIEW_FROM

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
            "awaiting_review_from": data.getlist("awaiting_review_from"),
            "organisation": data.getlist("organisation"),
            "sector": data.getlist("sector"),
            "country": data.getlist("country"),
            "status": data.getlist("status", ["20", "30"]),
            "region": data.getlist("region"),
        }
        return {k: v for k, v in cleaned_data.items() if v}
