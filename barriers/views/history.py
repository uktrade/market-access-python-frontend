from django.views.generic import TemplateView
from utils.api.client import MarketAccessAPIClient

from .mixins import BarrierMixin


class BarrierHistory(BarrierMixin, TemplateView):
    template_name = "barriers/history.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["history_items"] = self.get_full_history()
        return context_data

    def get_full_history(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        barrier_id = self.kwargs.get("barrier_id")
        full_history = client.barriers.get_full_history(barrier_id=barrier_id)
        full_history.sort(key=lambda object: object.date, reverse=True)
        return full_history
