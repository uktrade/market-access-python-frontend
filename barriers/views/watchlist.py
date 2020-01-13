from django.urls import reverse
from django.views.generic import FormView

from ..forms.search import BarrierSearchForm
from ..forms.watchlist import SaveWatchlistForm

from utils.metadata import get_metadata


class SaveWatchlist(FormView):
    """
    Save a watchlist either as a new watchlist or by replacing an existing one.

    Cleans the search parameters using BarrierSearchForm.
    """
    template_name = "barriers/watchlist/save.html"
    form_class = SaveWatchlistForm
    _search_form = None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        search_form = self.get_search_form()
        context_data['filters'] = search_form.get_filters()
        return context_data

    def get_search_form(self):
        if not self._search_form:
            self._search_form = BarrierSearchForm(
                metadata=get_metadata(),
                data=self.request.GET
            )
            self._search_form.full_clean()
        return self._search_form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        search_form = self.get_search_form()
        kwargs.update({
            'watchlists': self.request.session.get_watchlists(),
            'filters': {
                key: value
                for key, value in search_form.cleaned_data.items()
                if value
            },
        })
        return kwargs

    def form_valid(self, form):
        watchlists = form.save()
        self.request.session.set_watchlists(watchlists)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('barriers:dashboard')
