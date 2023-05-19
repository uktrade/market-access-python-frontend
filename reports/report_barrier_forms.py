from django import forms

from barriers.forms.mixins import APIFormMixin


class BarrierNameForm(APIFormMixin, forms.Form):
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


class BarrierStatusForm(APIFormMixin, forms.Form):
    confirm = forms.ChoiceField(
        label="Are these details correct?",
        choices={
            ("YES", "Yes"),
            ("NO", "No"),
        },
        widget=forms.RadioSelect,
    )


class BarrierSummaryForm(APIFormMixin, forms.Form):
    summary = forms.CharField(
        label="Describe the barrier",
        help_text=(
            "Include how the barrier is affecting the export or investment "
            "and why the barrier exists. For example, because of specific "
            "laws or measures, which government body imposed them and any "
            "political context; the HS code; and when the problem started."
        ),
        error_messages={"required": "Enter a description"},
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
