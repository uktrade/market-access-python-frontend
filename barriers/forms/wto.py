from django import forms
from django.conf import settings

from .mixins import APIFormMixin, DocumentMixin

from utils.api.client import MarketAccessAPIClient
from utils.forms import DayMonthYearField, YesNoBooleanField, RestrictedFileField


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


class WTOProfileForm(DocumentMixin, forms.Form):
    committee_notified = forms.ChoiceField(
        label="Committee notified of the barrier",
        choices=(),
        required=False,
    )
    committee_notification_link = forms.URLField(
        label="Committee notification",
        help_text=(
            "Enter a web link to the notification or attach a committee notification "
            "document"
        ),
        required=False,
    )
    committee_notification_document_id = forms.CharField(required=False)
    committee_notification_document = RestrictedFileField(
        label="Attach committee notification document",
        content_types=settings.ALLOWED_FILE_TYPES,
        max_upload_size=settings.FILE_MAX_SIZE,
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
    meeting_minutes_id = forms.CharField(required=False)
    meeting_minutes = RestrictedFileField(
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

    def __init__(self, id, metadata, wto_profile, *args, **kwargs):
        self.id = id
        self.metadata = metadata
        super().__init__(*args, **kwargs)
        self.set_committee_notified_choices()
        self.set_member_states_choices()
        self.set_committee_raised_in_choices()

        if not wto_profile.wto_has_been_notified:
            self.fields["committee_notified"].label = (
                "Which committee should be notified of the barrier?"
            )
            del self.fields["committee_notification_link"]
            del self.fields["committee_notification_document"]
            del self.fields["committee_notification_document_id"]
            del self.fields["meeting_minutes"]

    def get_committee_choices(self):
        """
        Grouped committee choices by committee group
        """
        return (("", "Select a committee"), ) + tuple(
            (
                group["name"],
                tuple((committee["id"], committee["name"])
                for committee in group["wto_committees"]),
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

    def clean_committee_notification_document(self):
        return self.validate_document("committee_notification_document")

    def clean_meeting_minutes(self):
        return self.validate_document("meeting_minutes")

    def clean_raised_date(self):
        if self.cleaned_data.get("raised_date"):
            return self.cleaned_data["raised_date"].isoformat()

    def save(self):
        client = MarketAccessAPIClient(self.token)
        wto_profile = {
            "committee_notified": self.cleaned_data.get("committee_notified"),
            "member_states": self.cleaned_data.get("member_states"),
            "committee_raised_in": self.cleaned_data.get("committee_raised_in"),
            "raised_date": self.cleaned_data.get("raised_date"),
            "case_number": self.cleaned_data.get("case_number", ""),
        }
        if "committee_notification_link" in self.fields:
            wto_profile["committee_notification_link"] = self.cleaned_data.get(
                "committee_notification_link", ""
            )
        if "committee_notification_document" in self.fields:
            wto_profile["committee_notification_document"] = self.cleaned_data.get(
                "committee_notification_document_id"
            )
        if "meeting_minutes" in self.fields:
            wto_profile["meeting_minutes"] = self.cleaned_data.get("meeting_minutes_id")
        client.barriers.patch(id=self.id, wto_profile=wto_profile)


class WTODocumentForm(DocumentMixin, forms.Form):
    """
    Form used to add documents via ajax. Only one field will be populated at a time.
    """
    committee_notification_document = RestrictedFileField(
        label="Attach committee notification document",
        content_types=settings.ALLOWED_FILE_TYPES,
        max_upload_size=settings.FILE_MAX_SIZE,
        required=False,
        multi_document=False,
    )
    meeting_minutes = RestrictedFileField(
        label="Committee meeting minutes",
        content_types=settings.ALLOWED_FILE_TYPES,
        max_upload_size=settings.FILE_MAX_SIZE,
        required=False,
        multi_document=False,
    )

    def save(self):
        if self.cleaned_data.get("committee_notification_document"):
            return self.upload_document("committee_notification_document")
        if self.cleaned_data.get("meeting_minutes"):
            return self.upload_document("meeting_minutes")
