from urllib.parse import urlencode

from django.forms import Form
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, View
from utils.api.client import MarketAccessAPIClient
from utils.metadata import get_metadata
from utils.pagination import PaginationMixin
from utils.tools import nested_sort

from ..forms.search import BarrierSearchForm


class SearchFormMixin:
    """
    Mixin for use with BarrierSearchForm.

    Retrieves search form data from the querystring.
    """

    def get_form_kwargs(self):
        return {
            "metadata": get_metadata(),
            "data": self.request.GET,
        }


class SearchFormView(SearchFormMixin, FormView):
    form_class = Form

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        form.full_clean()
        return self.render_to_response(self.get_context_data(form=form))


class BarrierSearch(PaginationMixin, SearchFormView):
    template_name = "barriers/search.html"
    form_class = BarrierSearchForm
    _client = None

    @property
    def client(self):
        if self._client is None:
            self._client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        return self._client

    def get_context_data(self, form, **kwargs):
        context_data = super().get_context_data(form=form, **kwargs)
        context_data.update(self.get_saved_search_context_data(form))
        barriers = self.get_barriers(form)
        metadata = get_metadata()
        context_data.update(
            {
                "barriers": barriers,
                "trading_blocs": metadata.get_trading_bloc_list(),
                "filters": form.get_readable_filters(with_remove_links=True),
                "pagination": self.get_pagination_data(object_list=barriers),
                "pageless_querystring": self.get_pageless_querystring(),
                "page": "search",
                "search_csv_downloaded": self.request.GET.get("search_csv_downloaded"),
                "search_csv_download_error": self.request.GET.get(
                    "search_csv_download_error"
                ),
            }
        )
        context_data = self.update_context_data_for_member(context_data, form)
        return context_data

    def get_barriers(self, form):
        return self.client.barriers.list(
            ordering="-reported_on",
            limit=self.get_pagination_limit(),
            offset=self.get_pagination_offset(),
            **form.get_api_search_parameters(),
        )

    def get_saved_search(self, form):
        if form.cleaned_data.get("search_id") is not None:
            saved_search_id = form.cleaned_data.get("search_id")
            return self.client.saved_searches.get(saved_search_id)

        filters = form.get_raw_filters()

        if filters == {"user": "1"}:
            return self.client.saved_searches.get("my-barriers")
        elif filters == {"team": "1"}:
            return self.client.saved_searches.get("team-barriers")

    def get_saved_search_context_data(self, form):
        context_data = {}
        saved_search = self.get_saved_search(form)
        if saved_search:
            context_data["saved_search"] = saved_search
            form_filters = form.get_raw_filters()
            context_data["have_filters_changed"] = nested_sort(
                form_filters
            ) != nested_sort(saved_search.filters)
            context_data["search_title"] = saved_search.name
            context_data["saved_search_created"] = self.request.session.pop(
                "saved_search_created",
                None,
            )
        return context_data

    def update_context_data_for_member(self, context_data, form):
        member_id = form.cleaned_data.get("member")
        if member_id:
            member = self.client.barriers.get_team_member(member_id)
            context_data["filters"]["member"]["readable_value"] = member["user"][
                "full_name"
            ]
            context_data["search_title"] = member["user"]["full_name"]
        return context_data

    def get_pageless_querystring(self):
        params = self.request.GET.copy()
        params.pop("page", None)
        return params.urlencode()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        form.full_clean()

        if "update_search" in request.POST and form.cleaned_data.get("search_id"):
            self.client.saved_searches.patch(
                id=str(form.cleaned_data.get("search_id")),
                filters=form.get_raw_filters(),
            )
        return self.render_to_response(
            self.get_context_data(form=form, saved_search_updated=True)
        )


class DownloadBarriers(SearchFormMixin, View):
    form_class = BarrierSearchForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(**self.get_form_kwargs())
        form.full_clean()
        search_parameters = form.get_api_search_parameters()
        current_url = request.build_absolute_uri()
        client = MarketAccessAPIClient(self.request.session["sso_token"])
        resp = client.barriers.get_email_csv(
            ordering="-reported_on", **search_parameters
        )

        search_page_url = reverse("barriers:search")
        search_page_params = {
            **search_parameters,
            "search_csv_downloaded": int(resp.get("success", False)),
            "search_csv_download_error": resp.get("reason", ""),
        }

        return HttpResponseRedirect(
            f"{search_page_url}?{urlencode(search_page_params)}"
        )
