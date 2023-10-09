import logging
from datetime import date, datetime

from dateutil.relativedelta import relativedelta
from django.views.generic import TemplateView

from utils.api.client import MarketAccessAPIClient
from utils.metadata import get_metadata

from .mixins import AnalyticsMixin, BarrierMixin

logger = logging.getLogger(__name__)


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
        active = self.request.GET.get("active", "barriers")
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        my_barriers_saved_search = client.saved_searches.get("my-barriers")
        team_barriers_saved_search = client.saved_searches.get("team-barriers")
        mentions = client.mentions.list()
        draft_barriers = client.reports.list()
        saved_searches = client.saved_searches.list()
        notification_exclusion = client.notification_exclusion.get()

        are_all_mentions_read: bool = not any(
            not mention.read_by_recipient for mention in mentions
        )

        graph_context_data = self.get_graphical_data()
        for graph_data in graph_context_data:
            # logger.critical("**************")
            # logger.critical(graph_data)
            # logger.critical("**************")
            context_data.update({f"{graph_data}": graph_context_data[graph_data]})

            # {{top_priority_status}}

        # logger.critical("**************")
        # logger.critical(context_data)
        # logger.critical("**************")

        context_data.update(
            {
                "page": "dashboard",
                "my_barriers_saved_search": my_barriers_saved_search,
                "team_barriers_saved_search": team_barriers_saved_search,
                "draft_barriers": draft_barriers,
                "saved_searches": saved_searches,
                "notification_exclusion": notification_exclusion,
                "mentions": mentions,
                "are_all_mentions_read": are_all_mentions_read,
                "new_mentions_count": len(
                    [mention for mention in mentions if not mention.read_by_recipient]
                ),
                "active": active,
            }
        )
        return context_data

    def get_graphical_data(self, **kwargs):
        # Function to gather data for potential dashboard graphs

        client = MarketAccessAPIClient(self.request.session.get("sso_token"))

        metadata = get_metadata()
        countries_metadata = metadata.get_country_list()

        resolved_barriers = client.barriers.list(**{"status": "4", "archived": "0"})

        graph_data_dictionary = {}

        i = 0
        month_list = []
        while i < 12:
            month_key = date.today() - relativedelta(months=i)
            month_key = month_key.strftime("%b %y")
            month_list.append(month_key)
            i = i + 1

        month_list.reverse()

        graph_data_dictionary["resolved_region_date_range"] = month_list

        for region in metadata.get_overseas_region_list():

            region_resolved_counts = []

            i = 0
            while i < 12:
                # Get date range for current month in loop
                first_day = (date.today() - relativedelta(months=i)).replace(day=1)
                last_day = (
                    (date.today() - relativedelta(months=i)).replace(day=1)
                    + relativedelta(months=1)
                    - relativedelta(days=1)
                )

                barrier_hits = 0
                for barrier in resolved_barriers:
                    for country in countries_metadata:
                        if barrier.location == country["name"]:
                            if country["overseas_region"]:
                                if country["overseas_region"]["id"] == region["id"]:
                                    if (
                                        datetime.date(barrier.status_date) >= first_day
                                        and datetime.date(barrier.status_date)
                                        <= last_day
                                    ):
                                        barrier_hits = barrier_hits + 1

                region_resolved_counts.append(barrier_hits)

                # Iterate loop
                i = i + 1

            region_name = region["name"].lower().replace(" ", "_").replace("-", "_")
            region_resolved_counts.reverse()
            graph_data_dictionary[
                f"resolved_barrier_count_{region_name}"
            ] = region_resolved_counts

            # graph_data_dictionary[f"resolved_barrier_cumulative_{region_name}"] = region_resolved_counts

        return graph_data_dictionary


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
            },
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
