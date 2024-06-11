import datetime

from django import forms
from django.template.loader import render_to_string

from barriers.constants import STATUSES, STATUSES_HELP_TEXT
from utils.forms import DayMonthYearField, SubformChoiceField, SubformMixin


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


class OpenInProgressForm(APIMappingMixin, forms.Form):
    """
    Subform of BarrierStatusForm
    """

    open_in_progress_summary = forms.CharField(
        label="Describe briefly the status of the barrier, including recent progress and any obstacles",
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

    part_resolved_date = DayMonthYearField(
        help_text="Enter '01' if you aren't sure of the day.",
        error_messages={
            "required": "Enter the date the barrier was partially resolved",
            "incomplete": "Enter the date the barrier was partially resolved",
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

    resolved_date = DayMonthYearField(
        help_text="Enter '01' if you aren't sure of the day.",
        error_messages={
            "required": "Enter the date the barrier was resolved",
            "incomplete": "Enter the date the barrier was resolved",
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
            STATUSES.OPEN_IN_PROGRESS: OpenInProgressForm,
            STATUSES.RESOLVED_IN_PART: ResolvedInPartForm,
            STATUSES.RESOLVED_IN_FULL: ResolvedInFullForm,
            STATUSES.DORMANT: DormantForm,
        },
    )

    def __init__(self, barrier, token, *args, **kwargs):
        self.barrier = barrier
        self.token = token
        kwargs["initial"] = {
            "status": barrier.status,
        }
        super().__init__(*args, **kwargs)

    def save(self):
        from utils.api.client import MarketAccessAPIClient

        client = MarketAccessAPIClient(self.token)
        subform = self.fields["status"].subform
        client.barriers.set_status(
            barrier_id=self.barrier.id,
            status=self.cleaned_data["status"],
            **subform.get_api_params(),
        )
