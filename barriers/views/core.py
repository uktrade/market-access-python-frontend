import logging
import urllib.parse

from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import redirect

from barriers.forms.search import BarrierSearchForm
from barriers.views.search import SearchFormView
from utils.api.client import MarketAccessAPIClient
from utils.metadata import get_metadata
from utils.pagination import PaginationMixin

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

    def get(self, *args, **kwargs):

        # Check to see if new default is being set
        default_home_page = self.request.GET.get("default", None)

        if default_home_page == "home":
            # set home as the default
            self.request.session["default"] = "home"
        elif default_home_page == "dashboard":
            # set home as the default
            self.request.session["default"] = "dashboard"

        # Check default dashboard current session
        current_default = self.request.session.get("default", None)

        if current_default == "home":
            return redirect("barriers:home")

        return super().get(*args, **kwargs)

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
        barrier_downloads = client.barrier_download.list()

        are_all_mentions_read: bool = not any(
            not mention.read_by_recipient for mention in mentions
        )

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
                "barrier_downloads": barrier_downloads,
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


class Home(AnalyticsMixin, SearchFormView, TemplateView, PaginationMixin):
    template_name = "barriers/home.html"
    utm_tags = {
        "en": {
            "utm_source": "notification-email",
            "utm_medium": "email",
            "utm_campaign": "dashboard",
        }
    }
    form_class = BarrierSearchForm

    # Let the pagination mixin know how many results the API will return per page
    pagination_limit = 5

    def get(self, form, *args, **kwargs):

        # Check to see if new default is being set
        default_home_page = self.request.GET.get("default", None)
        if default_home_page == "home":
            # set home as the default
            self.request.session["default"] = "home"
        elif default_home_page == "dashboard":
            # set home as the default
            self.request.session["default"] = "dashboard"

        # Check default dashboard current session
        current_default = self.request.session.get("default", None)
        if current_default == "dashboard":
            return redirect("barriers:dashboard")

        return super().get(form, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context_data = super().get_context_data(**kwargs)
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        mentions = client.mentions.list()
        are_all_mentions_read: bool = not any(
            not mention.read_by_recipient for mention in mentions
        )

        # Get page number for task list pagination from URL
        page_number = (
            self.request.GET.get("page") if self.request.GET.get("page") else 1
        )
        api_task_list_params = {
            "limit": self.get_pagination_limit(),
            "offset": self.get_pagination_offset(),
            "page": page_number,
        }
        # Get list of tasks for the user from the API
        task_list = client.dashboard_tasks.list(**api_task_list_params)

        params = form.get_api_search_parameters()

        query_string = ""
        for parameter in params:

            if isinstance(params[parameter], list):
                for value in params[parameter]:
                    query_string = (
                        query_string + f"&{urllib.parse.urlencode({parameter: value})}"
                    )
            else:
                query_string = (
                    query_string
                    + f"&{urllib.parse.urlencode({parameter: params[parameter]})}"
                )

        search_params = query_string

        summary_url = f"dashboard-summary?{search_params}"
        summary_stats = client.get(summary_url)

        metadata = get_metadata()

        context_data.update(
            {
                "page": "dashboard",
                "trading_blocs": metadata.get_trading_bloc_list(),
                "admin_areas": self.get_admin_areas_data(
                    metadata.get_admin_area_list()
                ),
                "countries_with_admin_areas": metadata.get_countries_with_admin_areas_list(),
                "mentions": mentions,
                "are_all_mentions_read": are_all_mentions_read,
                "new_mentions_count": len(
                    [mention for mention in mentions if not mention.read_by_recipient]
                ),
                "filters": form.get_readable_filters(True),
                "task_list": task_list,
                "summary_stats": summary_stats,
                "search_params": search_params,
            }
        )
        context_data["pagination"] = self.get_pagination_data(object_list=task_list)

        return context_data

    def get_admin_areas_data(self, admin_areas_metadata):
        # Admin area data works differently to both trading blocs and countries
        # We only want admin areas for specific countries and we need them formatted and
        # sorted in a particular way so the Javascript and HTML can display them correctly
        # in seperate drop down lists.
        filtered_areas = {}

        for area in admin_areas_metadata:
            country = area["country"]["id"]
            if filtered_areas.get(f"{country}") is None:
                filtered_areas[f"{country}"] = [
                    {"value": area["id"], "label": area["name"]}
                ]
            else:
                filtered_areas[f"{country}"].append(
                    {"value": area["id"], "label": area["name"]}
                )

        return filtered_areas


class GetDashboardSummary(View):
    def get(self, request, *args, **kwargs):
        client = MarketAccessAPIClient(request.session.get("sso_token"))
        summary_url = f"dashboard-summary?{request.GET.urlencode()}"
        resp = client.get(summary_url)
        return JsonResponse(resp)
