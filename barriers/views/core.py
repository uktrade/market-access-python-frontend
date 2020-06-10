from django.views.generic import TemplateView

from .mixins import AnalyticsMixin, BarrierMixin

from utils.api.client import MarketAccessAPIClient
from utils.metadata import get_metadata


class Dashboard(AnalyticsMixin, TemplateView):
    template_name = "barriers/dashboard.html"
    utm_tags = {
        "en": {
            "utm_source": "notification-email",
            "utm_medium": "email",
            "utm_campaign": "dashboard",
        }
    }

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


class BarrierDetail(AnalyticsMixin, BarrierMixin, TemplateView):
    template_name = "barriers/barrier_detail.html"
    include_interactions = True
    utm_tags = {
        "en": {
            "utm_source": "notification-email",
            "utm_medium": "email",
            "utm_campaign": {
                "n": "new-barriers",
                "u": "updated-barriers",
            }
        }
    }


class WhatIsABarrier(TemplateView):
    template_name = "barriers/what_is_a_barrier.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        metadata = get_metadata()
        context_data["goods"] = metadata.get_goods()
        context_data["services"] = metadata.get_services()
        return context_data
