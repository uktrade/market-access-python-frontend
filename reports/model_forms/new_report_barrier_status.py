from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from barriers.constants import STATUSES, STATUSES_HELP_TEXT
from barriers.forms.statuses import (
    DormantForm,
    OpenInProgressForm,
    OpenPendingForm,
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
        error_messages={"required": "Select a barrier scope"},
    )


class NewReportBarrierStatusForm(SubformMixin, NewReportBaseForm):
    """
    Form with subforms depending on the radio button selected
    """

    term = forms.ChoiceField(
        label="What type of barrier is it?",
        choices=BarrierTerms.choices,
        error_messages={"required": "Select a barrier scope"},
    )

    status = SubformChoiceField(
        label="Choose barrier status",
        choices=STATUSES,
        choices_help_text=STATUSES_HELP_TEXT,
        widget=forms.RadioSelect,
        error_messages={"required": "Choose a status"},
        subform_classes={
            STATUSES.OPEN_PENDING_ACTION: OpenPendingForm,
            STATUSES.OPEN_IN_PROGRESS: OpenInProgressForm,
            STATUSES.RESOLVED_IN_PART: ResolvedInPartForm,
            STATUSES.RESOLVED_IN_FULL: ResolvedInFullForm,
            STATUSES.DORMANT: DormantForm,
        },
    )

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        return {
            "term": str(barrier.term["id"]) if barrier.term else None,
            "status": str(barrier.status["id"]) if barrier.status else None,
            "sub_status": str(barrier.sub_status["code"])
            if barrier.sub_status
            else None,
            "status_summary": barrier.status_summary,
        }

    def serialize_data(self):
        subform = self.fields["status"].subform
        params = {
            "status": self.cleaned_data["status"],
            "term": self.cleaned_data["term"],
        }
        params.update(**subform.get_api_params())
        return params
