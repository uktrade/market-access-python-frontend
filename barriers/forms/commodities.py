from django import forms

from .mixins import APIFormMixin

from utils.api.client import MarketAccessAPIClient
from utils.exceptions import APIHttpException
from utils.forms import CommodityCodeWidget


class UpdateBarrierCommoditiesForm(forms.Form):
    code = forms.CharField(
        label="Enter one or more HS commodity codes",
        help_text=(
            "Enter your HS code below ignoring any spaces or full stops. "
            "You can also copy and paste multiple codes separated by commas "
            "into the first box (there is no limit). Only numbers and commas "
            "will be recognised, all other punctuation and characters will be ignored."
        ),
        error_messages={"required": "Enter an HS code"},
        widget=CommodityCodeWidget,
    )

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token")
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data["code"]
        client = MarketAccessAPIClient(self.token)
        try:
            self.commodity = client.commodities.get(id=code)
        except APIHttpException:
            raise forms.ValidationError("Code not found")
        return code
