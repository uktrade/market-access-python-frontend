from barriers.constants import ARCHIVED_REASON, PUBLIC_BARRIER_STATUSES
from .base import BaseHistoryItem, GenericHistoryItem
from .utils import PolymorphicBase
from utils.metadata import Statuses

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


class CountryHistoryItem(BaseHistoryItem):
    field = "country"
    field_name = "Public country"

    def get_value(self, value):
        return self.metadata.get_country(value)


class PublicViewStatusHistoryItem(BaseHistoryItem):
    field = "_public_view_status"
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
        return [
            self.metadata.get_sector(sector_id).get("name", "Unknown")
            for sector_id in value or []
        ]


class StatusHistoryItem(BaseHistoryItem):
    field = "status"
    field_name = "Public status"
    modifier = "status"

    def get_value(self, value):
        value["status_text"] = self.metadata.get_status_text(
            status_id=value["status"],
        )
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
        CountryHistoryItem,
        PublicViewStatusHistoryItem,
        SectorsHistoryItem,
        StatusHistoryItem,
        SummaryHistoryItem,
        TitleHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}
