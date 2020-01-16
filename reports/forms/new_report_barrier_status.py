from django import forms

from core.forms import SubFormsMixin, MonthYearForm


class BarrierProblemStatuses:
    SHORT_TERM = "SHORT_TERM"
    LONG_TERM = "LONG_TERM"

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
    """Form to capture Barrier Type"""
    # TODO: confirm what this field should be called
    #       using "status" for the time being
    status = forms.ChoiceField(
        label="What type of barrier is it?",
        choices=BarrierProblemStatuses.choices
    )


class BarrierStatuses:
    RESOLVED = "4"
    PARTIALLY_RESOLVED = "3"
    UNRESOLVED = "UNRESOLVED"

    @classmethod
    def choices(cls):
        choices = (
            (
                cls.RESOLVED,
                {
                    "label": "Yes, fully",
                    "hint": "It's still important to log resolved barriers",
                    "subforms": {
                        "resolved": {
                            "legend": "When was the barrier resolved?",
                        }
                    }
                }
            ),
            (
                cls.PARTIALLY_RESOLVED,
                {
                    "label": "Yes, partially",
                    "hint": "It's still important to log partially resolved barriers",
                    "subforms": {
                        "part_resolved": {
                            "legend": "When was the barrier partially resolved?",
                        }
                    }
                }
            ),
            (
                cls.UNRESOLVED,
                {
                    "label": "No",
                }
            ),
        )
        return choices


class NewReportBarrierStatus2Form(SubFormsMixin, forms.Form):
    """Form to capture Barrier Status"""
    status = forms.ChoiceField(
        label="Has the barrier been resolved?",
        choices=BarrierStatuses.choices
    )
    sub_forms = {
        "resolved": MonthYearForm,
        "part_resolved": MonthYearForm
    }
    ma_mapping = {
        "RESOLVED": BarrierStatuses.RESOLVED,
        "PART_RESOLVED": BarrierStatuses.PARTIALLY_RESOLVED
    }


class NewReportBarrierLocationForm(forms.Form):
    """Form to capture Barrier Location"""
    status = forms.ChoiceField(
        label="Which country has introduced the barrier?",
        choices=BarrierStatuses.choices
    )
