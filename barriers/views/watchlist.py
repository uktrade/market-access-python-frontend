from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView, View

from ..forms.search import BarrierSearchForm
from ..forms.watchlist import (
    EditWatchlistForm,
    RenameSavedSearchForm,
    NewSavedSearchForm,
)
from ..models import Watchlist

from utils.api.client import MarketAccessAPIClient
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
        context_data["filters"] = search_form.get_readable_filters()
        return context_data

    def get_search_form(self):
        if not self._search_form:
            self._search_form = BarrierSearchForm(
                metadata=get_metadata(), data=self.get_search_form_data()
            )
            self._search_form.full_clean()
        return self._search_form

    def get_search_form_data(self):
        return self.request.GET


class SavedSearchMixin:
    _saved_search = None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["saved_search"] = self.saved_search
        return context_data

    def get_saved_search(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        saved_search_id = self.kwargs.get("saved_search_id")
        return client.saved_searches.get(saved_search_id)

    @property
    def saved_search(self):
        if not self._saved_search:
            self._saved_search = self.get_saved_search()
        return self._saved_search


class NewSavedSearch(SearchFiltersMixin, FormView):
    template_name = "barriers/saved_searches/save.html"
    form_class = NewSavedSearchForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        search_form = self.get_search_form()
        kwargs["filters"] = search_form.get_raw_filters()
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs

    def form_valid(self, form):
        saved_search = form.save()
        return HttpResponseRedirect(self.get_success_url(saved_search=saved_search))

    def get_success_url(self, saved_search):
        return f"{reverse('barriers:find_a_barrier')}?search_id={saved_search.id}"


class DeleteSavedSearch(SavedSearchMixin, TemplateView):
    template_name = "barriers/saved_searches/delete.html"

    def post(self, request, *args, **kwargs):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        saved_search_id = self.kwargs.get("saved_search_id")
        client.saved_searches.delete(saved_search_id)
        return HttpResponseRedirect(reverse("barriers:dashboard"))


class RenameSavedSearch(SavedSearchMixin, SearchFiltersMixin, FormView):
    template_name = "barriers/saved_searches/rename.html"
    form_class = RenameSavedSearchForm

    def get(self, request, *args, **kwargs):
        if not self.saved_search:
            return HttpResponseRedirect(reverse("barriers:dashboard"))
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.saved_search:
            return HttpResponseRedirect(reverse("barriers:dashboard"))
        return super().post(request, *args, **kwargs)

    def get_initial(self):
        return {"name": self.saved_search.name}

    def get_search_form_data(self):
        return self.saved_search.filters

    def form_valid(self, form):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        saved_search_id = self.kwargs.get("saved_search_id")
        client.saved_searches.patch(
            id=saved_search_id,
            name=form.cleaned_data.get("name"),
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("barriers:dashboard")
