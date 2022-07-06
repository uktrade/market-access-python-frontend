from django import forms

from barriers.forms.commodities import UpdateBarrierCommoditiesForm
from utils.api.client import MarketAccessAPIClient


class NewReportUpdateBarrierCommoditiesForm(UpdateBarrierCommoditiesForm):
    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.reports.patch(id=self.barrier_id, commodities=self.commodities)

    def clean_codes(self):
        codes = super().clean_codes()
        if not codes:
            raise forms.ValidationError("No codes provided")
        return codes
