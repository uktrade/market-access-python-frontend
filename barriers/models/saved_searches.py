from urllib.parse import urlencode

from barriers.forms.search import BarrierSearchForm

from utils.metadata import get_metadata
from utils.models import APIModel


class SavedSearch(APIModel):
    _readable_filters = None

    @property
    def id(self):
        if self.filters == {"user": "1"}:
            return "my-barriers"
        elif self.filters == {"team": "1"}:
            return "team-barriers"
        return self.data.get("id")

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

    @property
    def notifications_text(self):
        if self.notify_about_additions:
            if self.notify_about_updates:
                return "New and updated"
            return "New"
        elif self.notify_about_updates:
            return "Updated"
        return "Off"
