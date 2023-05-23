from django import forms

from barriers.forms.mixins import APIFormMixin
from utils.forms import MultipleChoiceFieldWithHelpText, YesNoBooleanField

from reports.forms.new_report_barrier_about import BarrierSource


class BarrierNameForm(APIFormMixin, forms.Form):
    BS = BarrierSource()
    title = forms.CharField(
        label="Name this barrier",
        help_text=(
            "Include the name of the product, "
            "service or investment and the type of problem. "
            "For example, Import quotas for steel rods."
        ),
        max_length=255,
        error_messages={
            "max_length": "Name should be %(limit_value)d characters or less",
            "required": "Enter a name",
        },
    )

    product = forms.CharField(
        label="What product, service or investment is affected?",
        max_length=255,
        error_messages={
            "max_length": "Product, service or investment should be %(limit_value)d characters or fewer",
            "required": "Enter a product, service or investment",
        },
    )
    source = forms.ChoiceField(
        label="Who told you about the barrier?",
        choices=BS.choices(),
        error_messages={"required": "Select how you became aware of the barrier"},
    )
    other_source = forms.CharField(
        label="Please specify",
        required=False,
        max_length=255,
        error_messages={
            "required": "Select how you became aware of the barrier",
            "max_length": "Other source should be %(limit_value)d characters or fewer",
        },
    )
    tags = MultipleChoiceFieldWithHelpText(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        label="Is this issue caused by or related to any of the following?",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields["tags"].choices = tags


class BarrierSummaryForm(APIFormMixin, forms.Form):
    summary = forms.CharField(
        label="Describe the barrier",
        help_text="Include how the barrier is affecting the export or investment "
        "and why the barrier exists. For example, because of specific "
        "laws or measures, which government body imposed them and any "
        "political context; the HS code; and when the problem started.",
        error_messages={"required": "Enter a brief description for this barrier"},
    )
    is_summary_sensitive = YesNoBooleanField(
        label="Does the summary contain OFFICIAL-SENSITIVE information?",
        error_messages={
            "required": (
                "Indicate if summary contains OFFICIAL-SENSITIVE information or not"
            )
        },
    )
    next_steps_summary = forms.CharField(
        label="What steps will be taken to resolve the barrier?",
        help_text="Include all your agreed team actions.",
        required=False,
    )


class BarrierNameSummaryForm(BarrierNameForm, BarrierSummaryForm):
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
