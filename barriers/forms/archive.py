from django import forms
from django.template.loader import render_to_string

from barriers.constants import ARCHIVED_REASON
from utils.api.client import MarketAccessAPIClient
from utils.forms import SubformChoiceField, SubformMixin


class DuplicateBarrierForm(forms.Form):
    duplicate_explanation = forms.CharField(
        label="Please specify",
        widget=forms.Textarea,
        max_length=1000,
        required=True,
        error_messages={
            "max_length": "Reason should be %(limit_value)d characters or less",
            "required": "Enter a reason",
        },
    )

    def get_explanation(self):
        return self.cleaned_data["duplicate_explanation"]

    def as_html(self):
        template_name = "barriers/forms/archive/duplicate.html"
        return render_to_string(template_name, context={"form": self})


class NotABarrierForm(forms.Form):
    not_a_barrier_explanation = forms.CharField(
        label="Please specify",
        widget=forms.Textarea,
        max_length=1000,
        required=True,
        error_messages={
            "max_length": "Reason should be %(limit_value)d characters or less",
            "required": "Enter a reason",
        },
    )

    def get_explanation(self):
        return self.cleaned_data["not_a_barrier_explanation"]

    def as_html(self):
        template_name = "barriers/forms/archive/not_a_barrier.html"
        return render_to_string(template_name, context={"form": self})


class OtherForm(forms.Form):
    other_explanation = forms.CharField(
        label="Please specify",
        widget=forms.Textarea,
        max_length=1000,
        required=True,
        error_messages={
            "max_length": "Reason should be %(limit_value)d characters or less",
            "required": "Enter a reason",
        },
    )

    def get_explanation(self):
        return self.cleaned_data["other_explanation"]

    def as_html(self):
        template_name = "barriers/forms/archive/other.html"
        return render_to_string(template_name, context={"form": self})


class ArchiveBarrierForm(SubformMixin, forms.Form):
    reason = SubformChoiceField(
        label="Why are you archiving this barrier?",
        help_text=(
            "You can find archived barriers in search by "
            "selecting the 'Show' filter 'Only archived barriers'."
        ),
        choices=ARCHIVED_REASON,
        subform_classes={
            ARCHIVED_REASON.DUPLICATE: DuplicateBarrierForm,
            ARCHIVED_REASON.NOT_A_BARRIER: NotABarrierForm,
            ARCHIVED_REASON.OTHER: OtherForm,
        },
        widget=forms.RadioSelect,
        error_messages={"required": "Select duplicate, not a barrier or other"},
    )

    def __init__(self, id, token, *args, **kwargs):
        self.barrier_id = id
        self.token = token
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.barrier_id,
            archived=True,
            archived_reason=self.cleaned_data.get("reason"),
            archived_explanation=self.fields["reason"].subform.get_explanation(),
        )


class UnarchiveBarrierForm(forms.Form):
    reason = forms.CharField(
        label="Why are you unarchiving this barrier?",
        widget=forms.Textarea,
        max_length=1000,
        required=True,
        error_messages={
            "max_length": "Reason should be %(limit_value)d characters or less",
            "required": "Enter a reason",
        },
    )

    def __init__(self, id, token, *args, **kwargs):
        self.barrier_id = id
        self.token = token
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.barrier_id,
            archived=False,
            unarchived_reason=self.cleaned_data.get("reason"),
        )
