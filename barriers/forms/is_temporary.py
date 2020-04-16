from django import forms
from django.template.loader import render_to_string

from utils.api.client import MarketAccessAPIClient
from utils.forms import (
    MonthYearField, SubformChoiceField, SubformMixin,
)


class EndDateForm(forms.Form):
    has_end_date = forms.ChoiceField(
        label="Is there an end date?",
        choices=(
            ("yes", "Yes"),
            ("unknown", "I don't know"),
        ),
        widget=forms.RadioSelect,
        error_messages={"required": "Select ..."},
    )
    end_date = MonthYearField(
        label="Date the barrier will end",
        help_text=(
            "For example, 30 11 2020. If you don't know the day, please enter 1 for "
            "the first of the month."
        ),
        error_messages={
            "required": "Enter a month and year.",
            "incomplete": "Enter a month and year.",
        },
        required=False,
    )

    def __init__(self, *args, **kwargs):
        initial = kwargs.pop("initial", {})
        if initial.get("end_date"):
            initial["has_end_date"] = "yes"
        else:
            initial["has_end_date"] = "unknown"
        super().__init__(initial=initial, *args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        has_end_date = cleaned_data.get("has_end_date")
        end_date = cleaned_data.get("end_date")

        if has_end_date == "yes" and not end_date:
            self.add_error("end_date", "Enter the end date")

    def as_html(self):
        template_name = "barriers/edit/partials/end_date.html"
        return render_to_string(template_name, context={"form": self})

    def get_api_params(self):
        if self.cleaned_data.get("has_end_date") == "yes":
            return {"end_date": self.cleaned_data.get("end_date").isoformat()}
        return {"end_date": None}


class IsTemporaryForm(SubformMixin, forms.Form):
    is_temporary = SubformChoiceField(
        label="Is the barrier temporary?",
        choices=(
            ("yes", "Yes"),
            ("no", "No"),
            ("unknown", "I don't know"),
        ),
        widget=forms.RadioSelect,
        error_messages={"required": "Choose if the barrier is temporary or not"},
        subform_classes={
            "yes": EndDateForm,
        },
    )

    def __init__(self, barrier, token, *args, **kwargs):
        self.barrier = barrier
        self.token = token
        initial = kwargs.pop("initial", {})
        initial["is_temporary"] = self.get_is_temporary_value(
            initial.get("is_temporary")
        )
        super().__init__(initial=initial, *args, **kwargs)

    def get_is_temporary_value(self, is_temporary):
        if is_temporary is True:
            return "yes"
        elif is_temporary is False:
            return "no"
        return "unknown"

    def clean_is_temporary(self):
        data = self.cleaned_data["is_temporary"]
        if data == "yes":
            return True
        elif data == "no":
            return False

    def save(self):
        client = MarketAccessAPIClient(self.token)
        api_params = {
            "is_temporary": self.cleaned_data["is_temporary"],
            "end_date": None,
        }
        if hasattr(self.fields["is_temporary"], "subform"):
            subform = self.fields["is_temporary"].subform
            api_params.update(subform.get_api_params())

        client.barriers.patch(id=self.barrier.id, **api_params)
