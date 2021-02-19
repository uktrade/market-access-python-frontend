from django import forms

from barriers.forms.mixins import APIFormMixin
from utils.forms import YesNoBooleanField


class ArchiveAssessmentBaseForm(APIFormMixin, forms.Form):
    are_you_sure = YesNoBooleanField(
        label="Are you sure you want to archive this assessment?",
        error_messages={"required": "Enter yes or no"},
    )
    archived_reason = forms.CharField(
        label="Why are you archiving this assessment? (optional)",
        widget=forms.Textarea,
        max_length=500,
        required=False,
    )

    def archive_assessment(self):
        raise NotImplementedError

    def save(self):
        if self.cleaned_data.get("are_you_sure") is True:
            self.archive_assessment()
