import logging
from urllib.parse import urlencode

from barriers.forms.search import BarrierSearchForm
from utils.helpers import format_dict_for_url_querystring
from utils.metadata import get_metadata
from utils.models import APIModel

logger = logging.getLogger(__name__)


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
            search_form = BarrierSearchForm(
                metadata=get_metadata(),
                data=self.filters,
            )
            search_form.full_clean()
            self._readable_filters = search_form.get_readable_filters(
                with_remove_urls=False
            )
        return self._readable_filters

    @property
    def querystring(self):
        # In some instances, filters need reformatting before being encoded
        filters_for_encode = format_dict_for_url_querystring(
            self.filters, ["admin_areas"]
        )
        return urlencode(filters_for_encode, doseq=True)

    @property
    def notifications_text(self):
        if self.notify_about_additions:
            if self.notify_about_updates:
                return "NEW and UPDATED"
            return "NEW"
        elif self.notify_about_updates:
            return "UPDATED"
        return "Off"
