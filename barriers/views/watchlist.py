from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, View

from ..forms.search import BarrierSearchForm
from ..forms.watchlist import (
    EditWatchlistForm,
    RenameWatchlistForm,
    SaveWatchlistForm,
)

from utils.metadata import get_metadata


class SearchFiltersMixin:
    """
    Validates search filters and gets in readable form.

    Override get_search_form_data to use a different data source.
    """
    _search_form = None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        search_form = self.get_search_form()
        context_data['filters'] = search_form.get_readable_filters()
        return context_data

    def get_search_form(self):
        if not self._search_form:
            self._search_form = BarrierSearchForm(
                metadata=get_metadata(),
                data=self.get_search_form_data()
            )
            self._search_form.full_clean()
        return self._search_form

    def get_search_form_data(self):
        return self.request.GET


class SaveWatchlist(SearchFiltersMixin, FormView):
    """
    Save a watchlist either as a new watchlist or by replacing an existing one.

    Cleans the search parameters using BarrierSearchForm.
    """
    template_name = "barriers/watchlist/save.html"
    form_class = SaveWatchlistForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        search_form = self.get_search_form()
        kwargs.update({
            'watchlists': self.request.session.get_watchlists(),
            'filters': search_form.get_raw_filters()
        })
        return kwargs

    def form_valid(self, form):
        watchlists = form.save()
        self.request.session.set_watchlists(watchlists)
        index = form.get_new_watchlist_index()
        return HttpResponseRedirect(self.get_success_url(index=index))

    def get_success_url(self, index=0):
        if index:
            return f"{reverse('barriers:dashboard')}?list={index}"
        return reverse('barriers:dashboard')


class EditWatchlist(SearchFiltersMixin, FormView):
    template_name = "barriers/watchlist/edit.html"
    form_class = EditWatchlistForm

    def get(self, request, *args, **kwargs):
        self.watchlist = self.get_watchlist()
        if not self.watchlist:
            return HttpResponseRedirect(reverse('barriers:dashboard'))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.watchlist = self.get_watchlist()
        if not self.watchlist:
            return HttpResponseRedirect(reverse('barriers:dashboard'))
        return super().post(request, *args, **kwargs)

    def get_watchlist(self):
        index = self.request.GET.get('edit')
        return self.request.session.get_watchlist(index)

    def get_initial(self):
        return {'name': self.watchlist.get('name')}

    def form_valid(self, form):
        search_form = self.get_search_form()

        self.request.session.update_watchlist(
            index=int(self.request.GET.get('edit')),
            watchlist={
                'name': form.cleaned_data.get('name'),
                'filters': search_form.get_raw_filters(),
            },
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('barriers:dashboard')


class RemoveWatchlist(View):
    def get(self, request, *args, **kwargs):
        index = self.kwargs.get('index')
        request.session.delete_watchlist(index)
        return HttpResponseRedirect(reverse('barriers:dashboard'))


class RenameWatchlist(SearchFiltersMixin, FormView):
    template_name = "barriers/watchlist/rename.html"
    form_class = RenameWatchlistForm

    def get(self, request, *args, **kwargs):
        self.watchlist = self.get_watchlist()
        if not self.watchlist:
            return HttpResponseRedirect(reverse('barriers:dashboard'))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.watchlist = self.get_watchlist()
        if not self.watchlist:
            return HttpResponseRedirect(reverse('barriers:dashboard'))
        return super().post(request, *args, **kwargs)

    def get_watchlist(self):
        index = self.kwargs.get('index')
        return self.request.session.get_watchlist(index)

    def get_initial(self):
        return {'name': self.watchlist.get('name')}

    def get_search_form_data(self):
        return self.watchlist.get('filters')

    def form_valid(self, form):
        self.request.session.rename_watchlist(
            index=self.kwargs.get('index'),
            name=form.cleaned_data.get('name'),
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('barriers:dashboard')
