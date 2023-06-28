from django import forms

from barriers.constants import STATUSES, STATUSES_HELP_TEXT
from barriers.forms.statuses import (
    DormantForm,
    OpenInProgressForm,
    ResolvedInFullForm,
    ResolvedInPartForm,
)
from utils.forms import SubformChoiceField, SubformMixin


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
