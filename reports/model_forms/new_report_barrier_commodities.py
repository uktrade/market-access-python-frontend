from barriers.forms.commodities import UpdateBarrierCommoditiesForm
from utils.api.client import MarketAccessAPIClient


class NewReportUpdateBarrierCommoditiesForm(UpdateBarrierCommoditiesForm):
    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.reports.patch(id=self.barrier_id, commodities=self.commodities)
