import dateutil.parser

from barriers.constants import PUBLIC_BARRIER_STATUSES

from .base import BaseHistoryItem, GenericHistoryItem
from .utils import PolymorphicBase


class LocationHistoryItem(BaseHistoryItem):
    field = "country"
    field_name = "Public location"


class PublicViewStatusHistoryItem(BaseHistoryItem):
    field = "public_view_status"
    field_name = "Publish status"

    @property
    def show_summary(self):
        if self.new_value["public_view_status"]["id"] in (
            PUBLIC_BARRIER_STATUSES.UNKNOWN,
            PUBLIC_BARRIER_STATUSES.INELIGIBLE,
            PUBLIC_BARRIER_STATUSES.ELIGIBLE,
            PUBLIC_BARRIER_STATUSES.REVIEW_LATER,
        ):
            old_summary = self.old_value.get("public_eligibility_summary")
            new_summary = self.new_value.get("public_eligibility_summary")
            if new_summary and new_summary != old_summary:
                return True
        return False


class SectorsHistoryItem(BaseHistoryItem):
    field = "sectors"
    field_name = "Public sectors"

    def get_value(self, value):
        return {
            "all_sectors": value["all_sectors"],
            "sectors": [
                self.metadata.get_sector(sector_id).get("name", "Unknown")
                for sector_id in value["sectors"] or []
            ],
        }


class StatusHistoryItem(BaseHistoryItem):
    field = "status"
    field_name = "Public resolved status"
    modifier = "status"

    def get_value(self, value):
        value["status_text"] = self.metadata.get_status_text(
            status_id=value["status"],
        )
        if value["status_date"]:
            value["status_date"] = dateutil.parser.parse(value["status_date"])
        return value


class SummaryHistoryItem(BaseHistoryItem):
    field = "_summary"
    field_name = "Public summary"

    def get_value(self, value):
        return value or ""


class TitleHistoryItem(BaseHistoryItem):
    field = "_title"
    field_name = "Public title"


class PublicBarrierHistoryItem(PolymorphicBase):
    model = "public_barrier"
    key = "field"
    subclasses = (
        LocationHistoryItem,
        PublicViewStatusHistoryItem,
        SectorsHistoryItem,
        StatusHistoryItem,
        SummaryHistoryItem,
        TitleHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}
