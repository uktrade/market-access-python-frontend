from django.views.generic import FormView

from ..forms.watchlist import SaveWatchlistForm


class SaveWatchlist(FormView):
    template_name = "barriers/watchlist/save.html"
    form_class = SaveWatchlistForm
