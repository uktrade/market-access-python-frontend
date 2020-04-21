from django import forms
from django.conf import settings

from .mixins import APIFormMixin

from utils.api.client import MarketAccessAPIClient
from utils.forms import (
    DayMonthYearField,
    YesNoBooleanField,
    RestrictedFileField,
)


class WTOStatusForm(APIFormMixin, forms.Form):
    wto_has_been_notified = YesNoBooleanField(
        label="Has this measure been notified to the WTO?",
        error_messages={"required": "Enter yes or no"},
    )
    wto_should_be_notified = YesNoBooleanField(
        label="Should the measure be notified to the WTO?",
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("wto_has_been_notified") is False:
            if cleaned_data.get("wto_should_be_notified") is None:
                self.add_error(
                    "wto_should_be_notified", "Enter yes or no"
                )

    def get_api_params(self):
        wto_profile = {
            "wto_has_been_notified": self.cleaned_data.get("wto_has_been_notified"),
            "wto_should_be_notified": self.cleaned_data.get("wto_should_be_notified"),
        }
        return {"wto_profile": wto_profile}

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(id=self.id, **self.get_api_params())


class WTOProfileForm(APIFormMixin, forms.Form):
    committee_notified = forms.ChoiceField(
        label="Which committee should be notified of the barrier?",
        choices=(),
        required=False,
    )
    committee_notification_link = forms.URLField(
        label="Committee notification",
        help_text="Enter a web link to the notification or attach a committee notification document",
        required=False,
    )
    member_states = forms.MultipleChoiceField(
        label="Member state(s) that raised the barrier in a WTO committee",
        required=False,
    )
    committee_raised_in = forms.ChoiceField(
        label="WTO committee the barrier was raised in",
        choices=(),
        required=False,
    )
    committee_meeting_minutes = RestrictedFileField(
        label="Committee meeting minutes",
        content_types=settings.ALLOWED_FILE_TYPES,
        max_upload_size=settings.FILE_MAX_SIZE,
        required=False,
    )
    raised_date = DayMonthYearField(
        label="Date the barrier was raised in a bilateral meeting in Geneva",
        help_text="For example 30 11 2020",
        required=False,
    )
    case_number = forms.CharField(
        label="WTO dispute settlement case number for the barrier",
        required=False,
    )

    def __init__(self, metadata, *args, **kwargs):
        self.metadata = metadata
        super().__init__(*args, **kwargs)
        self.set_committee_notified_choices()
        self.set_member_states_choices()
        self.set_committee_raised_in_choices()

    def get_committee_choices(self):
        return (("", "Select a committee"), ) + tuple(
            (
                group["name"],
                tuple((committee["id"], committee["name"]) for committee in group["wto_committees"]),
            )
            for group in self.metadata.get_wto_committee_groups()
        )

    def set_member_states_choices(self):
        self.fields["member_states"].choices = [
            (country["id"], country["name"])
            for country in self.metadata.get_country_list()
        ]

    def set_committee_notified_choices(self):
        self.fields["committee_notified"].choices = self.get_committee_choices()

    def set_committee_raised_in_choices(self):
        self.fields["committee_raised_in"].choices = self.get_committee_choices()

    def clean_raised_date(self):
        if self.cleaned_data.get("raised_date"):
            return self.cleaned_data["raised_date"].isoformat()

    def get_api_params(self):
        return {"wto_profile": self.cleaned_data}

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(id=self.id, **self.get_api_params())
