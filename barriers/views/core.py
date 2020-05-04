from django.conf import settings
from django.http import StreamingHttpResponse
from django.views.generic import FormView, TemplateView, View

from ..forms.search import BarrierSearchForm
from .mixins import BarrierMixin

from utils.api.client import MarketAccessAPIClient
from utils.metadata import get_metadata
from utils.pagination import PaginationMixin
from utils.tools import nested_sort


class Dashboard(TemplateView):
    template_name = "barriers/dashboard.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        saved_searches = client.saved_searches.list()

        context_data.update(
            {
                "page": "dashboard",
                "saved_searches": saved_searches,
            }
        )
        return context_data


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


class FindABarrier(PaginationMixin, SearchFormMixin, FormView):
    template_name = "barriers/find_a_barrier.html"
    form_class = BarrierSearchForm

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        form.full_clean()
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, form, **kwargs):
        context_data = super().get_context_data(form=form, **kwargs)
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        barriers = client.barriers.list(
            ordering="-reported_on",
            limit=settings.API_RESULTS_LIMIT,
            offset=settings.API_RESULTS_LIMIT * (self.get_current_page() - 1),
            **form.get_api_search_parameters(),
        )

        context_data.update(
            {
                "barriers": barriers,
                "filters": form.get_readable_filters(with_remove_links=True),
                "pagination": self.get_pagination_data(
                    object_list=barriers,
                    limit=settings.API_RESULTS_LIMIT,
                ),
                "pageless_querystring": self.get_pageless_querystring(),
                "page": "find-a-barrier",
            }
        )

        if form.cleaned_data.get("search_id") is not None:
            saved_search_id = form.cleaned_data.get("search_id")
            saved_search = client.saved_searches.get(saved_search_id)
            context_data["saved_search"] = saved_search
            form_filters = form.get_raw_filters()
            context_data["have_filters_changed"] = nested_sort(
                form_filters
            ) != nested_sort(saved_search.filters)

        return context_data

    def get_pageless_querystring(self):
        params = self.request.GET.copy()
        params.pop("page", None)
        return params.urlencode()


class DownloadBarriers(SearchFormMixin, View):
    form_class = BarrierSearchForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(**self.get_form_kwargs())
        form.full_clean()
        search_parameters = form.get_api_search_parameters()

        client = MarketAccessAPIClient(self.request.session["sso_token"])
        file = client.barriers.get_csv(ordering="-reported_on", **search_parameters)

        response = StreamingHttpResponse(
            file.iter_content(), content_type=file.headers["Content-Type"]
        )
        response["Content-Disposition"] = file.headers["Content-Disposition"]
        return response


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
