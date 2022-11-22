from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from barriers.constants import STATUSES, STATUSES_HELP_TEXT
from barriers.forms.statuses import (
    DormantForm,
    OpenInProgressForm,
    ResolvedInFullForm,
    ResolvedInPartForm,
)
from reports.model_forms.base import NewReportBaseForm
from utils.forms import SubformChoiceField, SubformMixin

if TYPE_CHECKING:
    from reports.models import Report


class BarrierTerms:
    SHORT_TERM = "1"
    LONG_TERM = "2"

    @classmethod
    def choices(cls):
        choices = (
            (
                cls.SHORT_TERM,
                {
                    "label": "A procedural, short-term barrier",
                    "hint": "For example, overly complex customs paperwork",
                },
            ),
            (
                cls.LONG_TERM,
                {
                    "label": "A long-term strategic barrier",
                    "hint": "For example, a change of regulation",
                },
            ),
        )
        return choices


class NewReportBarrierTermForm(forms.Form):
    """Form to capture Barrier's term"""

    term = forms.ChoiceField(
        label="What type of barrier is it?",
        choices=BarrierTerms.choices,
        error_messages={"required": "Select a barrier type"},
    )


class NewReportBarrierStatusForm(SubformMixin, NewReportBaseForm):
    """
    Form with subforms depending on the radio button selected
    """

    status_to_form_class_map = {
        STATUSES.OPEN_IN_PROGRESS: OpenInProgressForm,
        STATUSES.RESOLVED_IN_PART: ResolvedInPartForm,
        STATUSES.RESOLVED_IN_FULL: ResolvedInFullForm,
        STATUSES.DORMANT: DormantForm,
    }

    term = forms.ChoiceField(
        label="What type of barrier is it?",
        choices=BarrierTerms.choices,
        error_messages={"required": "Select a barrier type"},
    )

    status = SubformChoiceField(
        label="Choose barrier status",
        choices=STATUSES,
        choices_help_text=STATUSES_HELP_TEXT,
        widget=forms.RadioSelect,
        error_messages={"required": "Select the barrier status"},
        subform_classes=status_to_form_class_map,
    )

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        base_initial = {
            "term": barrier.term,
            "status": str(barrier.status["id"]) if barrier.status else None,
            "sub_status": str(barrier.sub_status["code"])
            if barrier.sub_status
            else None,
            "sub_status_other": barrier.sub_status_other["id"]
            if barrier.sub_status_other
            else None,
            "status_summary": barrier.status_summary,
        }
        if not barrier.status:
            return base_initial

        if (
            not barrier.status["id"]
            in NewReportBarrierStatusForm.status_to_form_class_map
        ):
            # Skip if status is not addressed by subforms
            return base_initial

        # if a status is set, we need to get the subform class
        # and map the initial data to the custom field names of the
        # subform
        RelevantSubForm = NewReportBarrierStatusForm.status_to_form_class_map[
            str(barrier.status["id"])
        ]
        field_name_mapping = RelevantSubForm.api_mapping
        for sub_form_field, barrier_field in field_name_mapping.items():
            if barrier_field in base_initial:
                base_initial[sub_form_field] = base_initial[barrier_field]
        return base_initial

    def serialize_data(self):
        subform = self.fields["status"].subform
        params = {
            "status": self.cleaned_data["status"],
            "term": self.cleaned_data["term"],
        }
        params.update(**subform.get_api_params())
        return params
