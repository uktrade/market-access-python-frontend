from barriers.constants import ARCHIVED_REASON
from .base import BaseHistoryItem, GenericHistoryItem
from .utils import PolymorphicBase
from utils.metadata import Statuses

import dateutil.parser


class CategoriesHistoryItem(BaseHistoryItem):
    field = "categories"
    field_name = "Barrier categories"

    def get_value(self, value):
        category_names = [
            self.metadata.get_category(category).get("title")
            for category in value or []
        ]
        category_names.sort()
        return category_names


class LocationHistoryItem(BaseHistoryItem):
    field = "location"
    field_name = "Location"

    def get_value(self, value):
        return self.metadata.get_location_text(value["country"], value["admin_areas"])


class SectorsHistoryItem(BaseHistoryItem):
    field = "sectors"
    field_name = "Sectors affected"

    def get_value(self, value):
        return [
            self.metadata.get_sector(sector_id).get("name", "Unknown")
            for sector_id in value or []
        ]


class StatusHistoryItem(BaseHistoryItem):
    field = "status"
    field_name = "Status"
    modifier = "status"

    def get_value(self, value):
        if value["status_date"]:
            value["status_date"] = dateutil.parser.parse(value["status_date"])
        value["status_short_text"] = self.metadata.get_status_text(value["status"])
        value["status_text"] = self.metadata.get_status_text(
            status_id=value["status"],
            sub_status=value["sub_status"],
            sub_status_other=value["sub_status_other"],
        )
        value["is_resolved"] = value["status"] in (
            Statuses.RESOLVED_IN_PART,
            Statuses.RESOLVED_IN_FULL,
        )
        value["show_summary"] = value["status"] in (
            Statuses.OPEN_IN_PROGRESS,
            Statuses.UNKNOWN,
            Statuses.OPEN_PENDING_ACTION,
        )
        return value


class SummaryHistoryItem(BaseHistoryItem):
    field = "summary"
    field_name = "Summary"

    def get_value(self, value):
        return value or ""


class TitleHistoryItem(BaseHistoryItem):
    field = "title"
    field_name = "Title"


class PublicBarrierHistoryItem(PolymorphicBase):
    model = "public_barrier"
    key = "field"
    subclasses = (
        CategoriesHistoryItem,
        LocationHistoryItem,
        SectorsHistoryItem,
        StatusHistoryItem,
        SummaryHistoryItem,
        TitleHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}
