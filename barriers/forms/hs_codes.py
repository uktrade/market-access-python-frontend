from django import forms

from .mixins import APIFormMixin

from utils.api.client import MarketAccessAPIClient
from utils.forms import HSCodeWidget


class UpdateBarrierHSCodesForm(forms.Form):
    code = forms.CharField(
        label="Enter one or more HS commodity codes",
        help_text=(
            "Enter your HS code below ignoring any spaces or full stops. "
            "You can also copy and paste multiple codes separated by commas "
            "into the first box (there is no limit). Only numbers and commas "
            "will be recognised, all other punctuation and characters will be ignored."
        ),
        widget=HSCodeWidget,
    )
