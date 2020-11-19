from ..base import BaseHistoryItem, GenericHistoryItem
from ..documents import BaseDocumentsHistoryItem
from ..utils import PolymorphicBase


class BaseEconomicAssessmentHistoryItem(BaseHistoryItem):
    @property
    def is_edit(self):
        return self.data["old_value"] is not None

    def get_assessment_name(self, assessment_code):
        assessment_names = {
            "impact": "Economic assessment",
            "value_to_economy": "Value to UK Economy",
            "import_market_size": "Import Market Size",
            "export_value": "Value of currently affected UK exports",
            "commercial_value": "Commercial Value",
        }
        return assessment_names.get(assessment_code)

    @property
    def name(self):
        return self.get_assessment_name(self.field)


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


class CommercialValueHistoryItem(BaseEconomicAssessmentHistoryItem):
    field = "commercial_value"
    field_name = "Commercial value"


class CommercialValueExplanationHistoryItem(BaseHistoryItem):
    field = "commercial_value_explanation"
    field_name = "Commercial value explanation"

    def get_value(self, value):
        return value or ""


class DocumentsHistoryItem(BaseDocumentsHistoryItem):
    field = "documents"
    field_name = "Economic assessment: Supporting documents"


class ExplanationHistoryItem(BaseEconomicAssessmentHistoryItem):
    field = "explanation"
    field_name = "Economic assessment: Explanation"


class ExportValueHistoryItem(BaseEconomicAssessmentHistoryItem):
    field = "export_value"
    field_name = "UK export value"


class ImportMarketSizeHistoryItem(BaseEconomicAssessmentHistoryItem):
    field = "import_market_size"
    field_name = "Import market size"


class RatingHistoryItem(BaseEconomicAssessmentHistoryItem):
    field = "rating"
    field_name = "Economic assessment: Rating"

    def get_value(self, value):
        if value:
            return value.get("name")


class ReadyForApprovalHistoryItem(BaseEconomicAssessmentHistoryItem):
    field = "ready_for_approval"
    field_name = "Economic assessment: Ready for approval"

    def get_value(self, value):
        if value is True:
            return "Yes"
        elif value is False:
            return "No"


class ValueToEconomyHistoryItem(BaseEconomicAssessmentHistoryItem):
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
        CommercialValueHistoryItem,
        CommercialValueExplanationHistoryItem,
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
