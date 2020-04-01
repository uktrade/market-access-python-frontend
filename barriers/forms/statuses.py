import datetime

from django import forms
from django.template.loader import render_to_string

from barriers.constants import STATUSES, STATUSES_HELP_TEXT
from .mixins import APIFormMixin
from utils.api.client import MarketAccessAPIClient
from utils.forms import (
    ChoiceFieldWithHelpText, MonthYearField, SubformChoiceField, SubformMixin,
)


class UpdateBarrierStatusForm(APIFormMixin, forms.Form):
    status_date = MonthYearField(
        required=False,
        error_messages={
            "required": "Enter resolution date and include a month and year",
            "incomplete": "Enter resolution date and include a month and year.",
        },
    )
    status_summary = forms.CharField(
        label="Provide a summary of why this barrier is dormant",
        widget=forms.Textarea,
        error_messages={"required": "Enter a summary"},
    )

    def __init__(self, is_resolved, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_resolved = is_resolved
        if is_resolved:
            self.fields[
                "status_summary"
            ].label = "Provide a summary of how this barrier was resolved"
            self.fields["status_date"].required = True

    def validate_status_date(self):
        status_date = datetime.date(
            self.cleaned_data.get("year"), self.cleaned_data.get("month"), 1,
        )
        if status_date > datetime.date.today():
            self.add_error("month", "Resolution date must be this month or in the past")
            self.add_error("year", "Resolution date must be this month or in the past")
        else:
            self.cleaned_data["status_date"] = status_date

    def save(self):
        client = MarketAccessAPIClient(self.token)
        data = {"status_summary": self.cleaned_data["status_summary"]}

        if self.is_resolved:
            data["status_date"] = self.cleaned_data["status_date"].isoformat()

        client.barriers.patch(id=self.id, **data)


class UnknownForm(forms.Form):
    """
    Subform of BarrierStatusForm
    """

    unknown_summary = forms.CharField(
        label="Provide a summary of why this barrier is unknown",
        widget=forms.Textarea,
        error_messages={"required": "Enter a summary"},
    )

    def as_html(self):
        template_name = "barriers/forms/statuses/unknown.html"
        return render_to_string(template_name, context={"form": self})

    def get_api_params(self):
        return {
            "status_summary": self.cleaned_data["unknown_summary"],
        }


class OpenPendingForm(forms.Form):
    """
    Subform of BarrierStatusForm
    """

    CHOICES = [
        ("UK_GOVT", "UK government"),
        ("FOR_GOVT", "Foreign government"),
        ("BUS", "Affected business"),
        ("OTHER", "Other"),
    ]
    pending_type = forms.ChoiceField(
        label="Who is the action with?",
        choices=CHOICES,
        widget=forms.RadioSelect,
        error_messages={"required": "Select a pending action"},
    )
    pending_type_other = forms.CharField(label="Please specify", required=False,)
    pending_summary = forms.CharField(
        label="Provide a summary of why this barrier is pending action",
        widget=forms.Textarea,
        error_messages={"required": "Enter a summary"},
    )

    def as_html(self):
        template_name = "barriers/forms/statuses/open_pending.html"
        return render_to_string(template_name, context={"form": self})

    def clean(self):
        cleaned_data = super().clean()
        pending_type = cleaned_data.get("pending_type")
        pending_type_other = cleaned_data.get("pending_type_other")

        if pending_type == "OTHER" and not pending_type_other:
            self.add_error(
                "pending_type_other", "Enter a description for the pending action"
            )

    def get_api_params(self):
        params = {
            "status_summary": self.cleaned_data["pending_summary"],
            "sub_status": self.cleaned_data["pending_type"],
        }
        if self.cleaned_data.get("pending_type") == "OTHER":
            params.update({"sub_status_other": self.cleaned_data["pending_type_other"]})
        return params


class OpenInProgressForm(forms.Form):
    """
    Subform of BarrierStatusForm
    """

    reopen_summary = forms.CharField(
        label="Provide a summary of why this barrier is being reopened",
        widget=forms.Textarea,
        error_messages={"required": "Enter a summary"},
    )

    def as_html(self):
        template_name = "barriers/forms/statuses/open_in_progress.html"
        return render_to_string(template_name, context={"form": self})

    def get_api_params(self):
        return {
            "status_summary": self.cleaned_data["reopen_summary"],
        }


class ResolvedInPartForm(forms.Form):
    """
    Subform of BarrierStatusForm
    """

    part_resolved_date = MonthYearField(
        error_messages={
            "required": "Enter resolution date and include a month and year",
            "incomplete": "Enter resolution date and include a month and year.",
        },
    )
    part_resolved_summary = forms.CharField(
        label="Provide a summary of how this barrier was partially resolved",
        widget=forms.Textarea,
        error_messages={"required": "Enter a summary"},
    )

    def as_html(self):
        template_name = "barriers/forms/statuses/resolved_in_part.html"
        return render_to_string(template_name, context={"form": self})

    def get_api_params(self):
        return {
            "status_summary": self.cleaned_data["part_resolved_summary"],
            "status_date": self.cleaned_data["part_resolved_date"].isoformat(),
        }


class ResolvedInFullForm(forms.Form):
    """
    Subform of BarrierStatusForm
    """

    resolved_date = MonthYearField(
        error_messages={
            "required": "Enter resolution date and include a month and year",
            "incomplete": "Enter resolution date and include a month and year.",
        },
    )
    resolved_summary = forms.CharField(
        label="Provide a summary of how this barrier was resolved",
        widget=forms.Textarea,
        error_messages={"required": "Enter a summary"},
    )

    def as_html(self):
        template_name = "barriers/forms/statuses/resolved_in_full.html"
        return render_to_string(template_name, context={"form": self})

    def get_api_params(self):
        return {
            "status_summary": self.cleaned_data["resolved_summary"],
            "status_date": self.cleaned_data["resolved_date"].isoformat(),
        }


class DormantForm(forms.Form):
    """
    Subform of BarrierStatusForm
    """

    dormant_summary = forms.CharField(
        label="Provide a summary of why this barrier is dormant",
        widget=forms.Textarea,
        error_messages={"required": "Enter a summary"},
    )

    def as_html(self):
        template_name = "barriers/forms/statuses/dormant.html"
        return render_to_string(template_name, context={"form": self})

    def get_api_params(self):
        return {"status_summary": self.cleaned_data["dormant_summary"]}


class BarrierChangeStatusForm(SubformMixin, forms.Form):
    """
    Form with subforms depending on the radio button selected
    """

    status = SubformChoiceField(
        label="Change barrier status",
        choices=STATUSES,
        choices_help_text=STATUSES_HELP_TEXT,
        widget=forms.RadioSelect,
        error_messages={"required": "Choose a status"},
        subform_classes={
            STATUSES.UNKNOWN: UnknownForm,
            STATUSES.OPEN_PENDING_ACTION: OpenPendingForm,
            STATUSES.OPEN_IN_PROGRESS: OpenInProgressForm,
            STATUSES.RESOLVED_IN_PART: ResolvedInPartForm,
            STATUSES.RESOLVED_IN_FULL: ResolvedInFullForm,
            STATUSES.DORMANT: DormantForm,
        },
    )

    def __init__(self, barrier, token, *args, **kwargs):
        self.barrier = barrier
        self.token = token
        super().__init__(*args, **kwargs)
        self.remove_current_status_from_choices()

    def remove_current_status_from_choices(self):
        self.fields["status"].choices = [
            choice
            for choice in self.fields["status"].choices
            if choice[0] != self.barrier.status["id"]
        ]

    def save(self):
        client = MarketAccessAPIClient(self.token)
        subform = self.fields["status"].subform
        client.barriers.set_status(
            barrier_id=self.barrier.id,
            status=self.cleaned_data["status"],
            **subform.get_api_params(),
        )
