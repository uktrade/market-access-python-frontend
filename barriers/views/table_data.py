from django.http import JsonResponse
from django.views import View

from barriers.views.mixins import AjaxOnlyMixin
from utils.api.client import MarketAccessAPIClient


class BarrierTableData(AjaxOnlyMixin, View):
    def get(self, request, table_name, *args, **kwargs):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        table_data = client.barriers.get_table_data(table_name)
        return JsonResponse({"data": table_data})
