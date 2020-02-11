from django import forms

from core.forms import SubFormsMixin, MonthYearForm


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


class NewReportBarrierStatusForm(SubFormsMixin, forms.Form):
    """Form to capture Barrier's status"""
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

    @property
    def resolved_date(self):
        if self.cleaned_data["status"] == BarrierStatuses.UNRESOLVED:
            return ""
        else:
            resolved_date = None
            prefix = "resolved"
            if self.cleaned_data["status"] == BarrierStatuses.PARTIALLY_RESOLVED:
                prefix = f"part_{prefix}"
            month = self.cleaned_data.get(f"{prefix}_month")
            year = self.cleaned_data.get(f"{prefix}_year")
            if month and year:
                resolved_date = f"{year}-{month}-01"
            return resolved_date

    @property
    def is_resolved(self):
        if self.cleaned_data["status"] == BarrierStatuses.UNRESOLVED:
            return False
        else:
            return True

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("status"):
            cleaned_data["is_resolved"] = self.is_resolved
            cleaned_data["resolved_date"] = self.resolved_date
        return self.cleaned_data
