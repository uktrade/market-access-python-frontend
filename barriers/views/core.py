from urllib.parse import urlencode

from django.conf import settings
from django.http import StreamingHttpResponse
from django.views.generic import FormView, TemplateView, View

from ..forms.search import BarrierSearchForm
from .mixins import BarrierMixin

from utils.api_client import MarketAccessAPIClient
from utils.metadata import get_metadata
from utils.tools import nested_sort


class Dashboard(TemplateView):
    template_name = "barriers/dashboard.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        barriers = []
        watchlists = self.request.session.get_watchlists()

        if watchlists:
            watchlist_index = self.get_watchlist_index()
            selected_watchlist = watchlists[watchlist_index]
            selected_watchlist.setdefault('is_current', True)

            sort = self.request.GET.get('sort', '-modified_on')
            client = MarketAccessAPIClient(self.request.session['sso_token'])
            barriers = client.barriers.list(
                ordering=sort,
                **selected_watchlist.get_api_params()
            )

            context_data.update({
                'watchlist_index': watchlist_index,
                'watchlist_querystring': urlencode(
                    selected_watchlist.filters,
                    doseq=True,
                ),
                'sort_field': sort.lstrip('-'),
                'sort_descending': sort.startswith('-'),
            })

        context_data.update({
            'page': 'dashboard',
            'watchlists': watchlists,
            'barriers': barriers,
            'can_add_watchlist': (
                len(watchlists) < settings.MAX_WATCHLIST_LENGTH
            ),
        })
        return context_data

    def get_watchlist_index(self):
        """
        Get list index from querystring and ensure it's a valid number
        """
        try:
            list_index = int(self.request.GET.get('list', 0))
        except ValueError:
            return 0

        if list_index not in range(0, settings.MAX_WATCHLIST_LENGTH):
            return 0

        return list_index

    def get_search_form_data(self):
        return self.watchlist.filters


class SearchFormMixin:
    """
    Mixin for use with BarrierSearchForm.

    Retrieves search form data from the querystring.
    """
    def get_form_kwargs(self):
        return {
            'metadata': get_metadata(),
            'data': self.request.GET,
        }


class FindABarrier(SearchFormMixin, FormView):
    template_name = "barriers/find_a_barrier.html"
    form_class = BarrierSearchForm

    def get_context_data(self, form, **kwargs):
        context_data = super().get_context_data(form=form, **kwargs)
        client = MarketAccessAPIClient(self.request.session.get('sso_token'))
        barriers = client.barriers.list(
            ordering="-reported_on",
            limit=100,
            offset=0,
            **form.get_api_search_parameters(),
        )

        context_data.update({
            'barriers': barriers,
            'filters': form.get_readable_filters(with_remove_links=True),
            'page': 'find-a-barrier',
        })

        if form.cleaned_data.get('edit') is not None:
            watchlist_index = form.cleaned_data.get('edit')
            watchlist = self.request.session.get_watchlist(watchlist_index)
            form_filters = form.get_raw_filters()
            context_data['have_filters_changed'] = (
                nested_sort(form_filters) != nested_sort(watchlist.filters)
            )

        return context_data

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        form.full_clean()
        return self.render_to_response(self.get_context_data(form=form))


class DownloadBarriers(SearchFormMixin, View):
    form_class = BarrierSearchForm

    def get(self, request, *args, **kwargs):
        form = self.form_class(**self.get_form_kwargs())
        form.full_clean()
        search_parameters = form.get_api_search_parameters()

        client = MarketAccessAPIClient(self.request.session['sso_token'])
        file = client.barriers.get_csv(**search_parameters)

        response = StreamingHttpResponse(
            file.iter_content(),
            content_type=file.headers['Content-Type']
        )
        response['Content-Disposition'] = file.headers['Content-Disposition']
        return response


class BarrierDetail(BarrierMixin, TemplateView):
    template_name = "barriers/barrier_detail.html"
    include_interactions = True

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['add_company'] = settings.ADD_COMPANY
        return context_data


class WhatIsABarrier(TemplateView):
    template_name = "barriers/what_is_a_barrier.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        metadata = get_metadata()
        context_data['goods'] = metadata.get_goods()
        context_data['services'] = metadata.get_services()
        return context_data
