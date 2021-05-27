from django import forms

from barriers.constants import STATUSES, STATUSES_HELP_TEXT
from barriers.forms.statuses import (
    DormantForm,
    OpenInProgressForm,
    OpenPendingForm,
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
                    "hint": "These are issues that can be resolved fairly quickly and can be routine tasks. For example, a shipment is stuck in customs due to incorrect customs documentation, this is cleared once the proper paperwork is submitted.",
                },
            ),
            (
                cls.LONG_TERM,
                {
                    "label": "A long-term strategic barrier",
                    "hint": "These issues usually cannot be fixed quickly without a change in regulations or the business environment. For example, a ban on British food products as they don’t meet the countries new food safety regulations.

",
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
