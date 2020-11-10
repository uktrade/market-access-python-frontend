import re

from django import forms

from utils.api.client import MarketAccessAPIClient
from utils.exceptions import APIHttpException
from utils.forms import CommodityCodeWidget, MultipleValueField


class CommodityLookupForm(forms.Form):
    code = forms.CharField(
        label="Enter a commodity code (also known as an HS code)",
        help_text=(
            "Enter your commodity code below ignoring any spaces or full stops. "
            "You can also copy and paste multiple codes separated by commas "
            "into the first box (there is no limit). Only numbers and commas "
            "will be recognised, all other punctuation and characters will be ignored."
        ),
        error_messages={"required": "Enter a commodity code"},
        widget=CommodityCodeWidget,
    )
    location = forms.ChoiceField(
        label="Which location are the commodity codes from?",
        choices=[],
        error_messages={"required": "Select a location"},
    )

    def __init__(self, locations, *args, **kwargs):
        self.token = kwargs.pop("token")
        super().__init__(*args, **kwargs)
        self.fields["location"].choices = tuple([
            (location["id"], location["name"]) for location in locations
        ])

    def clean_code(self):
        code = self.cleaned_data["code"]
        return code[:10].ljust(10, "0")

    def clean(self):
        cleaned_data = super().clean()
        code = cleaned_data.get("code")
        location = cleaned_data.get("location")

        if not code or not location:
            return

        client = MarketAccessAPIClient(self.token)
        try:
            hs6_code = code[:6].ljust(10, "0")
            commodity = client.commodities.get(id=hs6_code)
            self.commodity = commodity.create_barrier_commodity(code=code, location=location)
        except APIHttpException:
            raise forms.ValidationError("Code not found")

    def get_commodity_data(self):
        return self.commodity.to_dict()


class MultiCommodityLookupForm(forms.Form):
    codes = forms.CharField()
    location = forms.ChoiceField(
        label="Which location are the HS commodity codes from?",
        choices=[],
        error_messages={"required": "Select a location"},
    )

    def __init__(self, locations, *args, **kwargs):
        self.token = kwargs.pop("token")
        super().__init__(*args, **kwargs)
        self.fields["location"].choices = tuple([
            (location["id"], location["name"]) for location in locations
        ])

    def clean_codes(self):
        codes = self.cleaned_data["codes"]
        codes = re.sub(r"[^/\d,;]", "", codes).replace(";", ",").strip(",")
        cleaned_codes = [code[:10].ljust(10, "0") for code in codes.split(",")]
        return list(set(cleaned_codes))

    def clean(self):
        cleaned_data = super().clean()
        codes = cleaned_data.get("codes")
        location = cleaned_data.get("location")

        if not codes or not location:
            return

        hs6_codes = [code[:6].ljust(10, "0") for code in codes]

        client = MarketAccessAPIClient(self.token)
        try:
            commodity_lookup = {
                commodity.code: commodity
                for commodity in client.commodities.list(codes=",".join(hs6_codes))
            }
        except APIHttpException:
            raise forms.ValidationError("Code not found")

        self.commodities = []
        for code in codes:
            hs6_code = code[:6].ljust(10, "0")
            commodity = commodity_lookup.get(hs6_code)
            if not commodity:
                continue
            barrier_commodity = commodity.create_barrier_commodity(code=code, location=location)
            self.commodities.append(barrier_commodity)

    def get_commodity_data(self):
        return [commodity.to_dict() for commodity in self.commodities]


class UpdateBarrierCommoditiesForm(forms.Form):
    codes = MultipleValueField(required=False)
    countries = MultipleValueField(required=False)
    trading_blocs = MultipleValueField(required=False)

    def __init__(self, barrier_id, token, *args, **kwargs):
        self.barrier_id = str(barrier_id)
        self.token = token
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        codes = cleaned_data["codes"]
        countries = cleaned_data["countries"]
        trading_blocs = cleaned_data["trading_blocs"]
        self.commodities = []
        for index, code in enumerate(codes):
            try:
                self.commodities.append({
                    "code": code,
                    "country": countries[index] or None,
                    "trading_bloc": trading_blocs[index],
                })
            except IndexError:
                raise forms.ValidationError("Code/country mismatch")
        return codes

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(id=self.barrier_id, commodities=self.commodities)
