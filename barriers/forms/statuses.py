import datetime

from django import forms
from django.template.loader import render_to_string

from barriers.constants import STATUSES, STATUSES_HELP_TEXT
from utils.forms import MonthYearField, SubformChoiceField, SubformMixin

from .mixins import APIFormMixin


class APIMappingMixin:
    api_mapping = {}

    def __init__(self, *args, **kwargs):
        initial = kwargs.get("initial")
        if initial:
            for form_field, api_field in self.api_mapping.items():
                if api_field in initial:
                    initial[form_field] = initial.pop(api_field)
        return super().__init__(*args, **kwargs)

    def get_api_params(self):
        params = {}
        for form_field, api_field in self.api_mapping.items():
            value = self.cleaned_data.get(form_field)
            if isinstance(value, datetime.date):
                value = value.isoformat()
            params[api_field] = value
        return params


class UnknownForm(APIMappingMixin, forms.Form):
    """
    Subform of BarrierStatusForm
    """

    unknown_summary = forms.CharField(
        label="Describe briefly why this barrier status is unknown",
        widget=forms.Textarea,
        error_messages={"required": "Enter a description"},
    )
    api_mapping = {"unknown_summary": "status_summary"}

    def as_html(self):
        template_name = "barriers/forms/statuses/unknown.html"
        return render_to_string(template_name, context={"form": self})


# class OpenPendingForm(APIMappingMixin, forms.Form):
#     """
#     Subform of BarrierStatusForm
#     """

#     CHOICES = [
#         ("UK_GOVT", "UK government"),
#         ("FOR_GOVT", "Foreign government"),
#         ("BUS", "Affected business"),
#         ("OTHER", "Other"),
#     ]
#     pending_type = forms.ChoiceField(
#         label="Who is due to take action?",
#         choices=CHOICES,
#         widget=forms.RadioSelect,
#         error_messages={"required": "Select who is due to take action"},
#     )
#     pending_type_other = forms.CharField(
#         label="Please specify",
#         required=False,
#     )
#     pending_summary = forms.CharField(
#         label="Describe briefly why this barrier is pending action",
#         widget=forms.Textarea,
#         error_messages={"required": "Enter a description"},
#     )
#     api_mapping = {
#         "pending_type": "sub_status",
#         "pending_type_other": "sub_status_other",
#         "pending_summary": "status_summary",
#     }

#     def __init__(self, *args, **kwargs):
#         kwargs.pop("barrier", None)
#         super().__init__(*args, **kwargs)

#     def as_html(self):
#         template_name = "barriers/forms/statuses/open_pending.html"
#         return render_to_string(template_name, context={"form": self})

#     def clean(self):
#         cleaned_data = super().clean()
#         pending_type = cleaned_data.get("pending_type")
#         pending_type_other = cleaned_data.get("pending_type_other")

#         if pending_type == "OTHER" and not pending_type_other:
#             self.add_error("pending_type_other", "Enter who is due to take action")

#     def get_api_params(self):
#         params = super().get_api_params()
#         if params["sub_status"] != "OTHER":
#             del params["sub_status_other"]
#         return params


class OpenInProgressForm(APIMappingMixin, forms.Form):
    """
    Subform of BarrierStatusForm
    """

    open_in_progress_summary = forms.CharField(
        label="Describe briefly why work on this barrier is in progress",
        widget=forms.Textarea,
        error_messages={"required": "Enter a description"},
    )
    api_mapping = {"open_in_progress_summary": "status_summary"}

    def __init__(self, *args, **kwargs):
        kwargs.pop("barrier", None)
        super().__init__(*args, **kwargs)

    def as_html(self):
        template_name = "barriers/forms/statuses/open_in_progress.html"
        return render_to_string(template_name, context={"form": self})


class ResolvedInPartForm(APIMappingMixin, forms.Form):
    """
    Subform of BarrierStatusForm
    """

    def __init__(self, *args, **kwargs):
        kwargs.pop("barrier", None)
        super().__init__(*args, **kwargs)

    part_resolved_date = MonthYearField(
        error_messages={
            "required": "Enter date barrier was part resolved",
            "incomplete": "Enter date barrier was part resolved",
        },
    )
    part_resolved_summary = forms.CharField(
        label="Describe briefly how this barrier was partially resolved",
        widget=forms.Textarea,
        error_messages={"required": "Enter a description"},
    )
    api_mapping = {
        "part_resolved_summary": "status_summary",
        "part_resolved_date": "status_date",
    }

    def as_html(self):
        template_name = "barriers/forms/statuses/resolved_in_part.html"
        return render_to_string(template_name, context={"form": self})


class ResolvedInFullForm(APIMappingMixin, forms.Form):
    """
    Subform of BarrierStatusForm
    """

    resolved_date = MonthYearField(
        error_messages={
            "required": "Enter date barrier was resolved",
            "incomplete": "Enter date barrier was resolved",
        },
    )
    resolved_summary = forms.CharField(
        label="Describe briefly how this barrier was fully resolved",
        widget=forms.Textarea,
        error_messages={"required": "Enter a description"},
    )
    api_mapping = {
        "resolved_summary": "status_summary",
        "resolved_date": "status_date",
    }

    def __init__(self, *args, **kwargs):
        kwargs.pop("barrier", None)
        super().__init__(*args, **kwargs)

    def as_html(self):
        template_name = "barriers/forms/statuses/resolved_in_full.html"
        return render_to_string(template_name, context={"form": self})


class DormantForm(APIMappingMixin, forms.Form):
    """
    Subform of BarrierStatusForm
    """

    dormant_summary = forms.CharField(
        label="Describe briefly why this barrier is dormant",
        widget=forms.Textarea,
        error_messages={"required": "Enter a description"},
    )
    api_mapping = {
        "dormant_summary": "status_summary",
    }

    def __init__(self, *args, **kwargs):
        kwargs.pop("barrier", None)
        super().__init__(*args, **kwargs)

    def as_html(self):
        template_name = "barriers/forms/statuses/dormant.html"
        return render_to_string(template_name, context={"form": self})


class UpdateBarrierStatusForm(APIFormMixin, forms.Form):
    status_date = MonthYearField(
        required=False,
        error_messages={
            "required": "Enter resolution date and include a month and year",
            "incomplete": "Enter resolution date and include a month and year.",
        },
    )
    status_summary = forms.CharField(
        label="Describe briefly why this barrier is dormant",
        widget=forms.Textarea,
        error_messages={"required": "Enter a description"},
    )
    status = SubformChoiceField(
        label="Change barrier status",
        choices=STATUSES,
        choices_help_text=STATUSES_HELP_TEXT,
        widget=forms.RadioSelect,
        error_messages={"required": "Select the barrier status"},
        subform_classes={
            # STATUSES.OPEN_PENDING_ACTION: OpenPendingForm,
            STATUSES.OPEN_IN_PROGRESS: OpenInProgressForm,
            STATUSES.RESOLVED_IN_PART: ResolvedInPartForm,
            STATUSES.RESOLVED_IN_FULL: ResolvedInFullForm,
            STATUSES.DORMANT: DormantForm,
        },
    )

    def __init__(self, barrier, is_resolved, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_resolved = is_resolved
        self.barrier = barrier
        # self.token = token
        if is_resolved:
            self.fields[
                "status_summary"
            ].label = "Describe briefly how this barrier was resolved"
            self.fields["status_date"].required = True
        self.remove_current_status_from_choices()

    def remove_current_status_from_choices(self):
        self.fields["status"].choices = [
            choice
            for choice in self.fields["status"].choices
            if choice[0] != self.barrier.status["id"]
        ]

    def validate_status_date(self):
        status_date = datetime.date(
            self.cleaned_data.get("year"),
            self.cleaned_data.get("month"),
            1,
        )
        if status_date > datetime.date.today():
            self.add_error("month", "Date resolved must be this month or in the past")
            self.add_error("year", "Date resolved must be this month or in the past")
        else:
            self.cleaned_data["status_date"] = status_date

    def save(self):
        # to avoid circular imports
        from utils.api.client import MarketAccessAPIClient

        client = MarketAccessAPIClient(self.token)
        data = {"status_summary": self.cleaned_data["status_summary"]}

        if self.is_resolved:
            data["status_date"] = self.cleaned_data["status_date"].isoformat()

        client.barriers.patch(id=self.id, **data)
        subform = self.fields["status"].subform
        client.barriers.set_status(
            barrier_id=self.barrier.id,
            status=self.cleaned_data["status"],
            **subform.get_api_params(),
        )


class BarrierChangeStatusForm(SubformMixin, forms.Form):
    """
    Form with subforms depending on the radio button selected
    """

    status = SubformChoiceField(
        label="Change barrier status",
        choices=STATUSES,
        choices_help_text=STATUSES_HELP_TEXT,
        widget=forms.RadioSelect,
        error_messages={"required": "Select the barrier status"},
        subform_classes={
            # STATUSES.OPEN_PENDING_ACTION: OpenPendingForm,
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
        # self.remove_current_status_from_choices()

    def remove_current_status_from_choices(self):
        self.fields["status"].choices = [
            choice
            for choice in self.fields["status"].choices
            if choice[0] != self.barrier.status["id"]
        ]

    def save(self):
        from utils.api.client import MarketAccessAPIClient

        client = MarketAccessAPIClient(self.token)
        subform = self.fields["status"].subform
        client.barriers.set_status(
            barrier_id=self.barrier.id,
            status=self.cleaned_data["status"],
            **subform.get_api_params(),
        )
