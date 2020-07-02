from django import forms

from .mixins import APIFormMixin

from utils.api.client import MarketAccessAPIClient
from utils.forms import YesNoBooleanField


class PublicEligibilityForm(APIFormMixin, forms.Form):
    public_eligibility = YesNoBooleanField(
        label="Can this barrier be made public?",
        choices=(
            ("yes", "Yes, it can be viewed by the public"),
            ("no", "No"),
        ),
        error_messages={"required": "Enter yes or no"},
    )
    allowed_summary = forms.CharField(
        label="Why is it allowed to be public? (optional)",
        widget=forms.Textarea,
        max_length=250,
        required=False,
    )
    not_allowed_summary = forms.CharField(
        label="Why is it not allowed to be public? (optional)",
        widget=forms.Textarea,
        max_length=250,
        required=False,
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
        error_messages={"required": "Enter a title"},
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        # TODO: Patch the public barrier


class PublishSummaryForm(APIFormMixin, forms.Form):
    summary = forms.CharField(
        label="Summary",
        widget=forms.Textarea,
        max_length=250,
        error_messages={"required": "Enter a summary"},
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        # TODO: Patch the public barrier


class MarkAsReadyForm(APIFormMixin, forms.Form):
    def save(self):
        client = MarketAccessAPIClient(self.token)
        print("Marking as ready")
        # TODO: Patch the public barrier


class PublishForm(APIFormMixin, forms.Form):
    not_sensitive = forms.BooleanField(
        label=(
            "I confirm this barrier does not contain OFFICIAL-SENSITIVE information "
            "and is suitable for public view"
        ),
        error_messages={
            "required": (
                "Confirm that this barrier does not contain OFFICIAL-SENSITIVE "
                "information"
            )
        },
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        print("Publishing")
        # TODO: Patch the public barrier
