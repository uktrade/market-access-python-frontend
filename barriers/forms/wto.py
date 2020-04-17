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
    wto_notified = YesNoBooleanField(
        label="Has this measure been notified to the WTO?",
        error_messages={"required": "Enter yes or no"},
    )
    wto_should_be_notified = YesNoBooleanField(
        label="Should the measure be notified to the WTO?",
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("wto_notified") is False:
            if cleaned_data.get("wto_should_be_notified") is None:
                self.add_error(
                    "wto_should_be_notified", "Enter yes or no"
                )

    def get_wto_status(self):
        if self.cleaned_data.get("wto_notified") is True:
            return "NOTIFIED"
        elif self.cleaned_data.get("wto_should_be_notified") is True:
            return "NOT_NOTIFIED"
        return "NO_NEED"

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(id=self.id, wto_status=self.get_wto_status())


class WTOInfoForm(APIFormMixin, forms.Form):
    committee_notified = forms.ChoiceField(
        label="Which committee should be notified of the barrier?",
        choices=(),
        required=False,
    )
    wto_should_be_notified = forms.MultipleChoiceField(
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
    wto_raised_date = DayMonthYearField(
        label="Date the barrier was raised in a bilateral meeting in Geneva",
        help_text="For example 30 11 2020"
    )
    wto_case_number = forms.CharField(
        label="WTO dispute settlement case number for the barrier",
    )
