from django.views.generic import TemplateView

from .mixins import BarrierMixin

from utils.api.client import MarketAccessAPIClient
from utils.metadata import get_metadata


class Dashboard(TemplateView):
    template_name = "barriers/dashboard.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        my_barriers_saved_search = client.saved_searches.get("my-barriers")
        team_barriers_saved_search = client.saved_searches.get("team-barriers")
        draft_barriers = client.reports.list()
        saved_searches = client.saved_searches.list()

        context_data.update(
            {
                "page": "dashboard",
                "my_barriers_saved_search": my_barriers_saved_search,
                "team_barriers_saved_search": team_barriers_saved_search,
                "draft_barriers": draft_barriers,
                "saved_searches": saved_searches,
            }
        )
        return context_data


class BarrierDetail(BarrierMixin, TemplateView):
    template_name = "barriers/barrier_detail.html"
    include_interactions = True


class WhatIsABarrier(TemplateView):
    template_name = "barriers/what_is_a_barrier.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        metadata = get_metadata()
        context_data["goods"] = metadata.get_goods()
        context_data["services"] = metadata.get_services()
        return context_data
