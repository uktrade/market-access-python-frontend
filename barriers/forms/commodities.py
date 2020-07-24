import re

from django import forms

from .mixins import APIFormMixin

from utils.api.client import MarketAccessAPIClient
from utils.exceptions import APIHttpException
from utils.forms import CommodityCodeWidget, MultipleValueField


class CommodityLookupForm(forms.Form):
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
    country = forms.ChoiceField(
        label="Which location are the HS commodity codes from?",
        choices=[],
        error_messages={"required": "Select a location"},
    )

    def __init__(self, countries, *args, **kwargs):
        self.token = kwargs.pop("token")
        super().__init__(*args, **kwargs)
        self.fields["country"].choices = tuple([
            (country["id"], country["name"]) for country in countries
        ])


    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data["code"]
        country = cleaned_data["country"]

        client = MarketAccessAPIClient(self.token)
        try:
            commodity = client.commodities.get(id=code)
            self.commodity = commodity.create_barrier_commodity(code=code, country_id=country)
        except APIHttpException:
            raise forms.ValidationError("Code not found")
        return code

    def get_commodity_data(self):
        return self.commodity.to_dict()


class MultiCommodityLookupForm(forms.Form):
    codes = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token")
        super().__init__(*args, **kwargs)

    def clean_codes(self):
        codes = self.cleaned_data["codes"]
        codes = re.sub('[^/\d,;]', '', codes).replace(";", ",")

        client = MarketAccessAPIClient(self.token)
        try:
            self.commodities = client.commodities.list(codes=codes)
        except APIHttpException:
            raise forms.ValidationError("Code not found")
        return codes

    def get_commodity_data(self):
        return [commodity.to_dict() for commodity in self.commodities]


class UpdateBarrierCommoditiesForm(forms.Form):
    codes = MultipleValueField(required=False)
    countries = MultipleValueField(required=False)

    def __init__(self, barrier_id, token, *args, **kwargs):
        self.barrier_id = barrier_id
        self.token = token
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        codes = cleaned_data["codes"]
        countries = cleaned_data["countries"]
        self.commodities = []
        for index, code in enumerate(codes):
            try:
                self.commodities.append({
                    "code": code,
                    "country": countries[index],
                })
            except IndexError:
                raise forms.ValidationError("Code/country mismatch")
        return codes

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(id=self.barrier_id, commodities=self.commodities)
