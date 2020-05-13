from urllib.parse import urlencode

from barriers.forms.search import BarrierSearchForm

from utils.metadata import get_metadata
from utils.models import APIModel


class SavedSearch(APIModel):
    _readable_filters = None

    @property
    def readable_filters(self):
        if self._readable_filters is None:
            search_form = BarrierSearchForm(metadata=get_metadata(), data=self.filters,)
            search_form.full_clean()
            self._readable_filters = search_form.get_readable_filters()
        return self._readable_filters

    @property
    def querystring(self):
        return urlencode(self.filters, doseq=True)
