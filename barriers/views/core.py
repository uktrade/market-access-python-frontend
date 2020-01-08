from urllib.parse import urlencode

from django.conf import settings
from django.http import StreamingHttpResponse
from django.views.generic import FormView, TemplateView, View

from ..forms.search import BarrierSearchForm
from .mixins import BarrierContextMixin

from utils.api_client import MarketAccessAPIClient
from utils.metadata import get_metadata


class Dashboard(TemplateView):
    template_name = "barriers/dashboard.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        sort = self.request.GET.get('sort', '-modified_on')
        default_user_profile_watchlists = {
            'watchLists': {
                'lists': [],    # this is where the watchlists live
                'version': 2
            }
        }
        watchlists = []
        barriers = []

        user_data = self.request.session['user_data']
        user_profile = user_data.get('user_profile', None)

        if user_profile:
            user_profile_watchlists = user_profile.get('watchList', default_user_profile_watchlists)
            watchlists = user_profile_watchlists.get('lists', ())
            if watchlists:
                watchlist_index = int(self.request.GET.get('list', 0))
                selected_watchlist = watchlists[watchlist_index]
                selected_watchlist.setdefault('is_current', True)

                filters = self.get_watchlist_params(selected_watchlist)
                client = MarketAccessAPIClient(self.request.session['sso_token'])
                barriers = client.barriers.list(
                    ordering=sort,
                    **filters
                )

        context_data.update({
            'page': 'dashboard',
            'watchlists': watchlists,
            'barriers': barriers,
            'can_add_watchlist': (
                len(watchlists) < settings.MAX_WATCHLIST_LENGTH
            ),
            'sort_field': sort.lstrip('-'),
            'sort_descending': sort.startswith('-'),
        })
        return context_data

    def get_watchlist_index(self, max_index):
        """
        Get list index from querystring and ensure it's a valid number
        """
        try:
            list_index = int(self.request.GET.get('list', 0))
        except ValueError:
            return 0

        if list_index not in range(0, max_index):
            return 0

        return list_index

    def get_watchlist_params(self, watchlist):
        filter_map = {
            'type': 'barrier_type',
            'search': 'text',
        }
        filters = {
            filter_map.get(name, name): value
            for name, value in watchlist.get('filters').items()
        }

        region = filters.pop('region', [])
        country = filters.pop('country', [])

        if country or region:
            filters['location'] = ",".join(country + region)

        if filters.get('sector'):
            filters['sector'] = ",".join(filters['sector'])

        if 'createdBy' in filters:
            created_by = filters.pop('createdBy')
            if '1' in created_by:
                filters['user'] = 1
            elif '2' in created_by:
                filters['team'] = 1

        return filters


class AddABarrier(TemplateView):
    template_name = "barriers/add_a_barrier.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update({
            'page': 'add-a-barrier',
        })
        return context_data


class SearchFormMixin:
    """
    Mixin for use with BarrierSearchForm.

    Retrieves search form data from the querystring.
    """
    def get_form_kwargs(self):
        return {
            'metadata': get_metadata(),
            'data': self.get_form_data(),
        }

    def get_form_data(self):
        """
        Get form data from the GET parameters.

        The 'search' field is a string, everything else should be a list.
        """
        data = {
            'search': self.request.GET.get('search'),
            'country': self.request.GET.getlist('country'),
            'sector': self.request.GET.getlist('sector'),
            'type': self.request.GET.getlist('type'),
            'region': self.request.GET.getlist('region'),
            'priority': self.request.GET.getlist('priority'),
            'status': self.request.GET.getlist('status'),
            'created_by': self.request.GET.getlist('created_by'),
        }
        return {k: v for k, v in data.items() if v}


class FindABarrier(SearchFormMixin, FormView):
    template_name = "barriers/find_a_barrier.html"
    form_class = BarrierSearchForm

    def get_context_data(self, form, **kwargs):
        context_data = super().get_context_data(**kwargs)
        client = MarketAccessAPIClient(self.request.session.get('sso_token'))
        barriers = client.barriers.list(
            ordering="-reported_on",
            limit=100,
            offset=0,
            **form.get_api_search_parameters(),
        )

        context_data.update({
            'barriers': barriers,
            'filters': self.get_filters(form),
            'page': 'find-a-barrier',
        })
        return context_data

    def get_filters(self, form):
        """
        Get the currently applied filters.

        Looks up the human-friendly value for fields with choices
        and calculates the url to remove each filter.
        """
        filters = {}

        for name, value in form.cleaned_data.items():
            remove_params = form.cleaned_data.copy()
            del remove_params[name]

            field = form.fields[name]
            filters[name] = {
                'label': field.label,
                'value': value,
                'remove_url': urlencode(remove_params, doseq=True),
            }
            if hasattr(field, 'choices'):
                field_lookup = dict(field.choices)
                filters[name]['value'] = ", ".join(
                    [field_lookup.get(x) for x in value]
                )

        return filters

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


class BarrierDetail(BarrierContextMixin, TemplateView):
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
