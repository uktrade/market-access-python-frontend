import copy
from urllib.parse import urlencode

from barriers.forms.search import BarrierSearchForm

from utils.metadata import get_metadata


class Watchlist:
    """
    Wrapper around user watchlist data
    """

    _readable_filters = None

    def __init__(self, name, filters, *args, **kwargs):
        self.name = name
        self.filters = self.clean_filters(filters)

    def clean_filters(self, filters):
        """
        Node saves the watchlist search term as a list for some reason.

        We now use user=1 and team=1 instead of created_by=[1,2] (or createdBy).
        """
        if "search" in filters and isinstance(filters["search"], list):
            try:
                filters["search"] = filters["search"][0]
            except IndexError:
                filters["search"] = ""

        created_by = filters.pop("createdBy", filters.pop("created_by", []))
        if "1" in created_by:
            filters["user"] = 1
        if "2" in created_by:
            filters["team"] = 1
        return filters

    def to_dict(self):
        return {
            "name": self.name,
            "filters": self.filters,
        }

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

    def get_api_params(self):
        """
        Transform watchlist filters into api parameters
        """
        filters = copy.deepcopy(self.filters)
        region = filters.pop("region", [])
        country = filters.pop("country", [])

        if country or region:
            filters["location"] = country + region

        created_by = filters.pop("createdBy", []) + filters.pop("created_by", [])
        if "1" in created_by:
            filters["user"] = 1
        elif "2" in created_by:
            filters["team"] = 1

        filter_map = {
            "type": "barrier_type",
            "search": "text",
        }

        api_params = {}
        for name, value in filters.items():
            mapped_name = filter_map.get(name, name)
            if isinstance(value, list):
                api_params[mapped_name] = ",".join(value)
            else:
                api_params[mapped_name] = value

        return api_params
