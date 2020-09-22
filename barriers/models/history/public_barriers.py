from barriers.constants import PUBLIC_BARRIER_STATUSES
from .base import BaseHistoryItem, GenericHistoryItem
from .utils import PolymorphicBase

import dateutil.parser


class CategoriesHistoryItem(BaseHistoryItem):
    field = "categories"
    field_name = "Public categories"

    def get_value(self, value):
        category_names = [
            self.metadata.get_category(category).get("title")
            for category in value or []
        ]
        category_names.sort()
        return category_names


class LocationHistoryItem(BaseHistoryItem):
    field = "location"
    field_name = "Public location"


class PublicViewStatusHistoryItem(BaseHistoryItem):
    field = "public_view_status"
    field_name = "Publish status"

    def get_value(self, value):
        try:
            return PUBLIC_BARRIER_STATUSES[value]
        except KeyError:
            return ""


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
    field = "summary"
    field_name = "Public summary"

    def get_value(self, value):
        return value or ""


class TitleHistoryItem(BaseHistoryItem):
    field = "title"
    field_name = "Public title"


class PublicBarrierHistoryItem(PolymorphicBase):
    model = "public_barrier"
    key = "field"
    subclasses = (
        CategoriesHistoryItem,
        LocationHistoryItem,
        PublicViewStatusHistoryItem,
        SectorsHistoryItem,
        StatusHistoryItem,
        SummaryHistoryItem,
        TitleHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}
