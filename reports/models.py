import operator

import dateutil.parser

from barriers.constants import STATUSES, Statuses
from utils.metadata import get_metadata
from utils.models import APIModel


class Report(APIModel):
    _metadata = None
    _progress = None

    @property
    def id(self):
        return self.data.get("id")

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = get_metadata()
        return self._metadata

    @property
    def resolved_text(self):
        if str(self.status["id"]) == STATUSES.RESOLVED_IN_FULL:
            return "In full"
        elif str(self.status["id"]) == STATUSES.RESOLVED_IN_PART:
            return "In part"
        return "No"

    @property
    def created_on(self):
        return dateutil.parser.parse(self.data["created_on"])

    @property
    def progress(self):
        if self._progress is None:
            self._progress = self.data.get("progress", [])
            self._progress.sort(key=operator.itemgetter("stage_code"))
        return self._progress

    def is_status(self, status_id: Statuses):
        if not self.status:
            return False
        return str(self.status["id"]) == status_id

    @property
    def sector_names(self):
        if self.all_sectors:
            return "All sectors"
        return ", ".join([sector.get("name") for sector in self.sectors])

    @property
    def source_display(self):
        return self.data.get("source", {}).get("name", "")

    @property
    def status_display(self):
        return self.data.get("status", {}).get("name", "")

    @property
    def sub_status_display(self):
        sub_status = self.data.get("sub_status", {}).get("name", "")
        if sub_status == "None":
            return None
        return sub_status

    @property
    def trade_direction_display(self):
        if self.data.get("trade_direction", {}):
            return self.data.get("trade_direction", {}).get("name", "")
        return ""

    @property
    def country_trading_bloc(self):
        # is the barrier tied to a country
        # and does that country have a trading bloc
        country = self.data.get("country", None)
        if not country:
            return False
        return country.get("trading_bloc", False)

    @property
    def get_admin_areas(self):
        if not self.country:
            return []
        return self.metadata.get_admin_areas_by_country(self.country["id"])
