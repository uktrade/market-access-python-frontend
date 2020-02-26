from django import forms
from django.template.loader import render_to_string

from .mixins import APIFormMixin

from utils.api.client import MarketAccessAPIClient
from utils.forms import ChoiceFieldWithHelpText


class DuplicateBarrierForm(forms.Form):
    duplicate_explanation = forms.CharField(
        label="Please specify",
        widget=forms.Textarea,
        max_length=1000,
        required=True,
        error_messages={
            'max_length': 'Explanation should be %(limit_value)d characters or fewer',
            'required': "Enter an explanation",
        }
    )

    def get_explanation(self):
        return self.cleaned_data["duplicate_explanation"]

    def as_html(self):
        template_name = "barriers/forms/archive/duplicate.html"
        return render_to_string(
            template_name,
            context={"form": self}
        )


class NotABarrierForm(forms.Form):
    not_a_barrier_explanation = forms.CharField(
        label="Please specify",
        widget=forms.Textarea,
        max_length=1000,
        required=True,
        error_messages={
            'max_length': 'Explanation should be %(limit_value)d characters or fewer',
            'required': "Enter an explanation",
        }
    )

    def get_explanation(self):
        return self.cleaned_data["not_a_barrier_explanation"]

    def as_html(self):
        template_name = "barriers/forms/archive/not_a_barrier.html"
        return render_to_string(
            template_name,
            context={"form": self}
        )


class OtherForm(forms.Form):
    other_explanation = forms.CharField(
        label="Please specify",
        widget=forms.Textarea,
        max_length=1000,
        required=True,
        error_messages={
            'max_length': 'Explanation should be %(limit_value)d characters or fewer',
            'required': "Enter an explanation",
        }
    )

    def get_explanation(self):
        return self.cleaned_data["other_explanation"]

    def as_html(self):
        template_name = "barriers/forms/archive/other.html"
        return render_to_string(
            template_name,
            context={"form": self}
        )


class ArchiveBarrierForm(forms.Form):
    CHOICES = [
        ("DUPLICATE", "Duplicate"),
        ("NOT_A_BARRIER", "Not a barrier"),
        ("OTHER", "Other"),
    ]
    reason = forms.ChoiceField(
        label="You must tell us why you are archiving this barrier",
        help_text=(
            "Archived barriers will only appear in search when the "
            "‘Show archived barriers’ filters is enabled."
        ),
        choices=CHOICES,
        widget=forms.RadioSelect,
        error_messages={"required": "Select a reason for archiving this barrier"},
    )
    subform_classes = {
        "DUPLICATE": DuplicateBarrierForm,
        "NOT_A_BARRIER": NotABarrierForm,
        "OTHER": OtherForm,
    }
    subforms = {}

    def __init__(self, id, token, *args, **kwargs):
        self.barrier_id = id
        self.token = token
        super().__init__(*args, **kwargs)

        data = kwargs.get("data")
        for value, subform_class in self.subform_classes.items():
            if data and data.get("reason") == value:
                self.subforms[value] = subform_class(data)
            else:
                self.subforms[value] = subform_class()

    def reason_choices(self):
        for value, name in self.fields["reason"].choices:
            yield {
                "value": value,
                "name": name,
                "subform": self.subforms[value],
            }

    def get_subform(self):
        return self.subforms.get(self.cleaned_data["reason"])

    @property
    def errors(self):
        form_errors = super().errors
        if self.is_bound and "reason" in self.cleaned_data:
            form_errors.update(self.get_subform().errors)
        return form_errors

    def save(self):
        client = MarketAccessAPIClient(self.token)
        subform = self.get_subform()
        client.barriers.patch(
            id=self.barrier_id,
            archived=True,
            archived_reason=self.cleaned_data.get("reason"),
            archived_explanation=subform.get_explanation(),
        )
