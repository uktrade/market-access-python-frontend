from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from utils.forms import TrueFalseBooleanField

if TYPE_CHECKING:
    from reports.models import Report


class NewReportBarrierSummaryForm(forms.Form):
    summary = forms.CharField(
        label="Describe the barrier",
        help_text=(
            "Include how the barrier is affecting the export or investment "
            "and why the barrier exists. For example, because of specific "
            "laws or measures, which government body imposed them and any "
            "political context; the HS code; and when the problem started."
        ),
        error_messages={"required": "Enter a brief description for this barrier"},
    )
    is_summary_sensitive = TrueFalseBooleanField(
        required=True,
        label="Does the summary contain OFFICIAL-SENSITIVE information?",
        error_messages={
            "required": (
                "Indicate if summary contains OFFICIAL-SENSITIVE information or not"
            )
        },
        widget=forms.RadioSelect(
            choices=[
                (True, "Yes"),
                (False, "No"),
            ]
        ),
    )

    @staticmethod
    def get_barrier_initial(barrier: Report):
        return {
            "summary": barrier.summary,
            "is_summary_sensitive": barrier.is_summary_sensitive or False,
        }
