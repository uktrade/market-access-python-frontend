from django import forms

from barriers.constants import STATUSES, STATUSES_HELP_TEXT
from barriers.forms.statuses import (
    OpenPendingForm,
    OpenInProgressForm,
    ResolvedInPartForm,
    ResolvedInFullForm,
    DormantForm,
)
from utils.forms import SubformChoiceField, SubformMixin


class BarrierProblemStatuses:
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
                }
            ),
            (
                cls.LONG_TERM,
                {
                    "label": "A long-term strategic barrier",
                    "hint": "For example, a change of regulation",
                }
            ),
        )
        return choices


class NewReportBarrierProblemStatusForm(forms.Form):
    """Form to capture Barrier's problem_status"""
    status = forms.ChoiceField(
        label="What type of barrier is it?",
        choices=BarrierProblemStatuses.choices,
        error_messages={'required': "Select a barrier scope"},
    )


class NewReportBarrierStatusForm(SubformMixin, forms.Form):
    """
    Form with subforms depending on the radio button selected
    """

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

    def get_api_params(self):
        subform = self.fields["status"].subform
        params = {"status": self.cleaned_data["status"]}
        params.update(**subform.get_api_params())
        return params
