from django import forms

from .mixins import APIFormMixin

from utils.api.client import MarketAccessAPIClient
from utils.forms import YesNoBooleanField


class PublishEligibilityForm(APIFormMixin, forms.Form):
    is_publishable = YesNoBooleanField(
        label="Is this barrier eligible for public view?",
        choices=(
            ("no", "No, this barrier is ineligible"),
            ("yes", "Yes, this barrier is eligible"),
        ),
        error_messages={"required": "Enter yes or no"},
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            is_publishable=self.cleaned_data.get("is_publishable"),
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
