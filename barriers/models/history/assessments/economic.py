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
    field_name = "Economic assessment - Supporting documents"


class ExplanationHistoryItem(BaseEconomicAssessmentHistoryItem):
    field = "explanation"
    field_name = "Economic assessment - explanation"


class ExportValueHistoryItem(BaseEconomicAssessmentHistoryItem):
    field = "export_value"
    field_name = "UK export value"


class ImportMarketSizeHistoryItem(BaseEconomicAssessmentHistoryItem):
    field = "import_market_size"
    field_name = "Import market size"


class RatingHistoryItem(BaseEconomicAssessmentHistoryItem):
    field = "rating"
    field_name = "Economic assessment - rating"


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
        CommercialValueHistoryItem,
        CommercialValueExplanationHistoryItem,
        DocumentsHistoryItem,
        ExplanationHistoryItem,
        ExportValueHistoryItem,
        ImportMarketSizeHistoryItem,
        RatingHistoryItem,
        ValueToEconomyHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}
