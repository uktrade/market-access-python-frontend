from django import forms

from barriers.forms.mixins import APIFormMixin
from utils.forms import MultipleChoiceFieldWithHelpText, YesNoBooleanField

from reports.forms.new_report_barrier_about import BarrierSource


class BarrierNameForm(APIFormMixin, forms.Form):
    BS = BarrierSource()
    title = forms.CharField(
        label="Barrier title",
        help_text=(
            """
            The title should be suitable for the public to read on GOV.UK. It will only be published once it has been reviewed internally. Include the product, service or investment and the type of problem. For example, Import quotas for steel rods.
            """
        ),
        max_length=255,
        error_messages={
            "max_length": "Name should be %(limit_value)d characters or less",
            "required": "Enter a barrier title",
        },
        initial="",
    )
    is_not_published_to_public = forms.ChoiceField(
        label="This barrier should not be published on GOV.UK",
        widget=forms.RadioSelect,
        choices=(
            ("yes", "Yes"),
            ("no", "No"),
        ),
        initial="no",
    )


class BarrierSummaryForm(APIFormMixin, forms.Form):
    summary = forms.CharField(
        label="Public barrier summary",
        help_text=(
            """
        Describe the barrier in a way that is suitable for the public to read on GOV.UK. The summary will only be published once it has been reviewed internally.
        """
        ),
        error_messages={"required": "Enter a public barrier summary"},
        initial="",
    )
    description = forms.CharField(
        label="Barrier description",
        widget=forms.Textarea,
        help_text=(
            """
        This description will only be used internally. Explain how the barrier is affecting trade, and why it exists. Where relevant include the specific laws or measures blocking trade, and any political context.
        """
        ),
        error_messages={"required": "Enter a barrier description"},
        initial="",
    )


class BarrierAboutForm(BarrierNameForm, BarrierSummaryForm):
    ...


class BarrierStatusForm(APIFormMixin, forms.Form):
    confirm = forms.ChoiceField(
        label="Are these details correct?",
        choices={
            ("YES", "Yes"),
            ("NO", "No"),
        },
        widget=forms.RadioSelect,
    )


class BarrierReviewForm(APIFormMixin, forms.Form):
    confirm = forms.ChoiceField(
        label="Are these details correct?",
        choices={
            ("YES", "Yes"),
            ("NO", "No"),
        },
        widget=forms.RadioSelect,
    )
