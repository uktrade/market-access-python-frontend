from django import forms

from barriers.forms.commodities import UpdateBarrierCommoditiesForm
from utils.api.client import MarketAccessAPIClient


class NewReportUpdateBarrierCommoditiesForm(UpdateBarrierCommoditiesForm):
    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.reports.patch(id=self.barrier_id, commodities=self.commodities)

    # def clean_codes(self):
    #     codes = self.cleaned_data["codes"]
    #     if not codes:
    #         raise forms.ValidationError("Please provide at least one HS code")
    #     return codes
