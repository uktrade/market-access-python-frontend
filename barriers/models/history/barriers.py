from barriers.constants import ARCHIVED_REASON
from .base import BaseHistoryItem
from .utils import PolymorphicBase
from utils.metadata import Statuses

import dateutil.parser


class ArchivedHistoryItem(BaseHistoryItem):
    field = "archived"
    field_name = "Archived"
    modifier = "archived"

    def __init__(self, data):
        super().__init__(data)

        if not self.new_value["archived"]:
            self.modifier = "unarchived"

    def get_value(self, value):
        if "archived_reason" in value:
            value["archived_reason"] = ARCHIVED_REASON[value["archived_reason"]]
        return value


class CategoriesHistoryItem(BaseHistoryItem):
    field = "categories"
    field_name = "Barrier categories"

    def get_value(self, value):
        category_names = [
            self.metadata.get_barrier_type(category).get("title")
            for category in value or []
        ]
        category_names.sort()
        return category_names


class CompaniesHistoryItem(BaseHistoryItem):
    field = "companies"
    field_name = "Companies"

    def get_value(self, value):
        return [company["name"] for company in value or []]


class DescriptionHistoryItem(BaseHistoryItem):
    field = "problem_description"
    field_name = "Summary"

    def get_value(self, value):
        return value or ""


class EUExitRelatedHistoryItem(BaseHistoryItem):
    field = "eu_exit_related"
    field_name = "Related to EU exit"

    def get_value(self, value):
        return self.metadata.get_eu_exit_related_text(value)


class LocationHistoryItem(BaseHistoryItem):
    field = "location"
    field_name = "Location"

    def get_value(self, value):
        return self.metadata.get_location_text(value["country"], value["admin_areas"])


class PriorityHistoryItem(BaseHistoryItem):
    field = "priority"
    field_name = "Priority"
    modifier = "priority"

    def get_value(self, value):
        value["priority"] = self.metadata.get_priority(value["priority"])
        return value


class ProductHistoryItem(BaseHistoryItem):
    field = "product"
    field_name = "Product, service or investment affected"


class ScopeHistoryItem(BaseHistoryItem):
    field = "problem_status"
    field_name = "Type"

    def get_value(self, value):
        return self.metadata.get_problem_status(value)


class SectorsHistoryItem(BaseHistoryItem):
    field = "sectors"
    field_name = "Sectors affected"

    def get_value(self, value):
        return [
            self.metadata.get_sector(sector_id).get("name", "Unknown")
            for sector_id in value or []
        ]


class SourceHistoryItem(BaseHistoryItem):
    field = "source"
    field_name = "Information source"

    def get_value(self, value):
        source = self.metadata.get_source(value["source"])
        if value["other_source"]:
            return f"{source} - {value['other_source']}"
        return source


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


class TitleHistoryItem(BaseHistoryItem):
    field = "barrier_title"
    field_name = "Title"


class BarrierHistoryItem(PolymorphicBase):
    """
    Polymorphic wrapper for HistoryItem classes
    """

    model = "barrier"
    key = "field"
    subclasses = (
        ArchivedHistoryItem,
        CategoriesHistoryItem,
        CompaniesHistoryItem,
        DescriptionHistoryItem,
        EUExitRelatedHistoryItem,
        LocationHistoryItem,
        ProductHistoryItem,
        PriorityHistoryItem,
        ScopeHistoryItem,
        SectorsHistoryItem,
        SourceHistoryItem,
        StatusHistoryItem,
        TitleHistoryItem,
    )
    class_lookup = {}
