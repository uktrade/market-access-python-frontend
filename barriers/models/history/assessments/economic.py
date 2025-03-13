from ..base import BaseHistoryItem, GenericHistoryItem
from ..documents import BaseDocumentsHistoryItem
from ..utils import PolymorphicBase


class ApprovedHistoryItem(BaseHistoryItem):
    field = "approved"
    field_name = "Economic assessment: Approval"

    def get_value(self, value):
        if value is True:
            return "Approved"
        elif value is False:
            return "Rejected"


class ArchivedHistoryItem(BaseHistoryItem):
    field = "archived"
    field_name = "Economic assessment: Archived"

    def get_value(self, value):
        if value is True:
            return "Archived"
        elif value is False:
            return "Unarchived"


class DocumentsHistoryItem(BaseDocumentsHistoryItem):
    field = "documents"
    field_name = "Economic assessment: Supporting documents"


class ExplanationHistoryItem(BaseHistoryItem):
    field = "explanation"
    field_name = "Economic assessment: Explanation"


class ExportValueHistoryItem(BaseHistoryItem):
    field = "export_value"
    field_name = "UK export value"


class ImportMarketSizeHistoryItem(BaseHistoryItem):
    field = "import_market_size"
    field_name = "Import market size"


class RatingHistoryItem(BaseHistoryItem):
    field = "rating"
    field_name = "Economic assessment: Rating"

    def get_value(self, value):
        if value:
            return value.get("name")


class ReadyForApprovalHistoryItem(BaseHistoryItem):
    field = "ready_for_approval"
    field_name = "Economic assessment: Ready for approval"

    def get_value(self, value):
        if value is True:
            return "Yes"
        elif value is False:
            return "No"


class ValueToEconomyHistoryItem(BaseHistoryItem):
    field = "value_to_economy"
    field_name = "Value to UK economy"


class EconomicAssessmentHistoryItem(PolymorphicBase):
    """
    Polymorphic wrapper for HistoryItem classes
    """

    model = "economic_assessment"
    key = "field"
    subclasses = (
        ArchivedHistoryItem,
        ApprovedHistoryItem,
        DocumentsHistoryItem,
        ExplanationHistoryItem,
        ExportValueHistoryItem,
        ImportMarketSizeHistoryItem,
        RatingHistoryItem,
        ReadyForApprovalHistoryItem,
        ValueToEconomyHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}


class PreliminaryAssessmentValueHistoryItem(BaseHistoryItem):
    field = "value"
    field_name = "Preliminary assessment value"


class PreliminaryAssessmentDetailsHistoryItem(BaseHistoryItem):
    field = "details"
    field_name = "Preliminary assessment details"


class PreliminaryAssessmentHistoryItem(PolymorphicBase):
    model = "preliminary_assessment"
    key = "field"
    subclasses = (
        PreliminaryAssessmentValueHistoryItem,
        PreliminaryAssessmentDetailsHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}
