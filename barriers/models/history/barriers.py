from barriers.constants import ARCHIVED_REASON
from .base import BaseHistoryItem
from .utils import PolymorphicBase
from utils.metadata import Statuses

import dateutil.parser


class ArchivedHistoryItem(BaseHistoryItem):
    field = "archived"
    field_name = "Archived"

    def __init__(self, data):
        super().__init__(data)
        self.archived = data["new_value"]

        if self.archived:
            self.modifier = "archived"
            archived_reason_code = data["field_info"].get("archived_reason")
            if archived_reason_code:
                self.archived_reason = ARCHIVED_REASON[archived_reason_code]

            self.archived_explanation = data["field_info"].get("archived_explanation")
        else:
            self.modifier = "unarchived"
            self.unarchived_reason = data["field_info"].get("unarchived_reason")

    def get_value(self, value):
        if "archived_reason" in value:
            value["archived_reason"] = ARCHIVED_REASON[value["archived_reason"]]
        return value


class CategoriesHistoryItem(BaseHistoryItem):
    field = "categories"
    field_name = "Barrier categories"

    def get_value(self, value):
        return [
            self.metadata.get_barrier_type(category).get("title")
            for category in value or []
        ]


class CompaniesHistoryItem(BaseHistoryItem):
    field = "companies"
    field_name = "Companies"

    def get_value(self, value):
        return [company["name"] for company in value or []]


class DescriptionHistoryItem(BaseHistoryItem):
    field = "problem_description"
    field_name = "Summary"


class EUExitRelatedHistoryItem(BaseHistoryItem):
    field = "eu_exit_related"
    field_name = "Related to EU exit"

    def get_value(self, value):
        return self.metadata.get_eu_exit_related_text(value)


class LocationHistoryItem(BaseHistoryItem):
    field = "location"
    field_name = "Location"

    def get_value(self, value):
        return self.metadata.get_location_text(value['country'], value['admin_areas'])


class PriorityHistoryItem(BaseHistoryItem):
    field = "priority"
    field_name = "Priority"
    modifier = "priority"

    @property
    def priority(self):
        return self.new_value

    @property
    def text(self):
        return self.data["field_info"]["priority_summary"]

    def get_value(self, value):
        return self.metadata.get_priority(value)


class ProductHistoryItem(BaseHistoryItem):
    field = "product"
    field_name = "Product, service or investment affected"


class ScopeHistoryItem(BaseHistoryItem):
    field = "problem_status"
    field_name = "Scope"

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
        return self.metadata.get_source(value)


class StatusHistoryItem(BaseHistoryItem):
    field = "status"
    field_name = "Status"
    modifier = "status"

    @property
    def event(self):
        return self.data["field_info"].get("event")

    @property
    def state(self):
        return {
            "from": self.metadata.get_status_text(self.data["old_value"]),
            "to": self.metadata.get_status_text(
                self.data["new_value"],
                self.data["field_info"].get("sub_status"),
                self.data["field_info"].get("sub_status_other"),
            ),
            "date": dateutil.parser.parse(self.data["field_info"]["status_date"]),
            "is_resolved": self.data["new_value"]
            in (Statuses.RESOLVED_IN_PART, Statuses.RESOLVED_IN_FULL,),
            "show_summary": self.data["new_value"]
            in (
                Statuses.OPEN_IN_PROGRESS,
                Statuses.UNKNOWN,
                Statuses.OPEN_PENDING_ACTION,
            ),
        }

    @property
    def text(self):
        return self.data["field_info"]["status_summary"]

    def get_value(self, value):
        return self.metadata.get_status_text(value)


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
