from barriers.constants import ARCHIVED_REASON

from utils.diff import diff_match_patch
from utils.metadata import get_metadata, Statuses
from utils.models import APIModel

import dateutil.parser


class BaseHistoryItem(APIModel):

    @property
    def date(self):
        return dateutil.parser.parse(self.data["date"])

    @property
    def new_value(self):
        return self.get_value(self.data["new_value"]) or ""

    @property
    def old_value(self):
        return self.get_value(self.data["old_value"]) or ""

    @property
    def diff(self):
        dmp = diff_match_patch()
        diffs = dmp.diff_main(self.old_value, self.new_value)
        dmp.diff_cleanupSemantic(diffs)
        return dmp.diff_prettyHtml(diffs)

    def get_value(self, value):
        return value


class TitleHistoryItem(BaseHistoryItem):
    field = "barrier_title"
    field_name = "Title"


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


class StatusHistoryItem(BaseHistoryItem):
    field = "status"
    field_name = "Status"
    modifier = "status"

    @property
    def event(self):
        return self.data["field_info"].get("event")

    @property
    def state(self):
        metadata = get_metadata()
        return {
            "from": metadata.get_status_text(self.data["old_value"]),
            "to": metadata.get_status_text(
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
        metadata = get_metadata()
        return metadata.get_status_text(value)


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
        metadata = get_metadata()
        return metadata.get_priority(value)


class AssessmentHistoryItem(BaseHistoryItem):

    @property
    def is_edit(self):
        return self.data["old_value"] is not None

    @property
    def name(self):
        metadata = get_metadata()
        return metadata.get_assessment_name(self.field)


class CompaniesHistoryItem(BaseHistoryItem):
    field = "companies"
    field_name = "Companies"

    def get_value(self, value):
        return [company["name"] for company in value or []]


class EUExitRelatedHistoryItem(BaseHistoryItem):
    field = "eu_exit_related"
    field_name = "Related to EU exit"

    def get_value(self, value):
        metadata = get_metadata()
        return metadata.get_eu_exit_related_text(value)


class DescriptionHistoryItem(BaseHistoryItem):
    field = "problem_description"
    field_name = "Summary"


class LocationHistoryItem(BaseHistoryItem):
    field = "location"
    field_name = "Location"

    def get_value(self, value):
        metadata = get_metadata()
        return metadata.get_location_text(value['country'], value['admin_areas'])


class ValueToEconomyHistoryItem(AssessmentHistoryItem):
    field = "value_to_economy"
    field_name = "Value to UK economy"


class CommercialValueHistoryItem(AssessmentHistoryItem):
    field = "commercial_value"
    field_name = "Commercial value"


class ExportValueHistoryItem(AssessmentHistoryItem):
    field = "export_value"
    field_name = "UK export value"


class ImportMarketSizeHistoryItem(AssessmentHistoryItem):
    field = "import_market_size"
    field_name = "Import market size"


class ExplanationHistoryItem(AssessmentHistoryItem):
    field = "explanation"
    field_name = "Economic assessment - explanation"


class ImpactHistoryItem(AssessmentHistoryItem):
    field = "impact"
    field_name = "Economic assessment - impact"

    def get_value(self, value):
        metadata = get_metadata()
        return metadata.get_impact_text(value)


class ProductHistoryItem(BaseHistoryItem):
    field = "product"
    field_name = "Product, service or investment affected"


class SourceHistoryItem(BaseHistoryItem):
    field = "source"
    field_name = "Information source"

    def get_value(self, value):
        metadata = get_metadata()
        return metadata.get_source(value)


class SectorsHistoryItem(BaseHistoryItem):
    field = "sectors"
    field_name = "Sectors affected"

    def get_value(self, value):
        metadata = get_metadata()
        return [
            metadata.get_sector(sector_id).get("name", "Unknown")
            for sector_id in value or []
        ]


class NoteHistoryItem(BaseHistoryItem):
    field = "text"
    field_name = "Notes"


class CategoriesHistoryItem(BaseHistoryItem):
    field = "categories"
    field_name = "Barrier categories"

    def get_value(self, value):
        metadata = get_metadata()
        return [
            metadata.get_barrier_type(category).get("title")
            for category in value or []
        ]


class TeamMemberHistoryItem(BaseHistoryItem):
    field = "team_member"
    field_name = "Barrier team"


class DocumentsHistoryItem(BaseHistoryItem):
    field = "documents"
    field_name = "Documents"

    def deleted_documents(self):
        new_documents = {v['id']: v for v in self.new_value}
        old_documents = {v['id']: v for v in self.old_value}
        deleted_ids = set(old_documents.keys()).difference(set(new_documents.keys()))
        return [old_documents[document_id] for document_id in deleted_ids]

    def added_documents(self):
        new_documents = {v['id']:v for v in self.new_value}
        old_documents = {v['id']:v for v in self.old_value}
        added_ids = set(new_documents.keys()).difference(set(old_documents.keys()))
        return [new_documents[document_id] for document_id in added_ids]

    def unchanged_documents(self):
        new_documents = {v['id']:v for v in self.new_value}
        old_documents = {v['id']:v for v in self.old_value}
        unchanged_ids = set(new_documents.keys()).intersection(set(old_documents.keys()))
        return [new_documents[document_id] for document_id in unchanged_ids]


class HistoryItem:
    """
    Polymorphic wrapper for HistoryItem classes
    """

    history_item_classes = (
        TitleHistoryItem, StatusHistoryItem, PriorityHistoryItem, ArchivedHistoryItem,
        EUExitRelatedHistoryItem, DescriptionHistoryItem,
        ValueToEconomyHistoryItem, ProductHistoryItem, SourceHistoryItem,
        SectorsHistoryItem, NoteHistoryItem, CategoriesHistoryItem,
        CompaniesHistoryItem, LocationHistoryItem, ExplanationHistoryItem,
        ImpactHistoryItem, ValueToEconomyHistoryItem, CommercialValueHistoryItem, ExportValueHistoryItem,
        ImportMarketSizeHistoryItem, TeamMemberHistoryItem, DocumentsHistoryItem,
    )
    class_lookup = {}

    def __new__(cls, data):
        if not cls.class_lookup:
            cls.init_class_lookup()

        history_item_class = cls.class_lookup.get(data["field"], BaseHistoryItem)
        return history_item_class(data)

    @classmethod
    def init_class_lookup(cls):
        for history_item_class in cls.history_item_classes:
            cls.class_lookup[history_item_class.field] = history_item_class
