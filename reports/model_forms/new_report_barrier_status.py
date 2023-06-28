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
