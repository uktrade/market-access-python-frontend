from .base import BaseHistoryItem
from .documents import BaseDocumentsHistoryItem
from .utils import PolymorphicBase


class BaseAssessmentHistoryItem(BaseHistoryItem):
    @property
    def is_edit(self):
        return self.data["old_value"] is not None

    @property
    def name(self):
        return self.metadata.get_assessment_name(self.field)


class CommercialValueHistoryItem(BaseAssessmentHistoryItem):
    field = "commercial_value"
    field_name = "Commercial value"


class ExplanationHistoryItem(BaseAssessmentHistoryItem):
    field = "explanation"
    field_name = "Economic assessment - explanation"


class ExportValueHistoryItem(BaseAssessmentHistoryItem):
    field = "export_value"
    field_name = "UK export value"


class ImpactHistoryItem(BaseAssessmentHistoryItem):
    field = "impact"
    field_name = "Economic assessment - impact"

    def get_value(self, value):
        return self.metadata.get_impact_text(value)


class ImportMarketSizeHistoryItem(BaseAssessmentHistoryItem):
    field = "import_market_size"
    field_name = "Import market size"


class DocumentsHistoryItem(BaseDocumentsHistoryItem):
    field = "documents"
    field_name = "Economic assessment - Supporting documents"


class ValueToEconomyHistoryItem(BaseAssessmentHistoryItem):
    field = "value_to_economy"
    field_name = "Value to UK economy"


class AssessmentHistoryItem(PolymorphicBase):
    """
    Polymorphic wrapper for HistoryItem classes
    """

    model = "assessment"
    key = "field"
    subclasses = (
        CommercialValueHistoryItem,
        DocumentsHistoryItem,
        ExplanationHistoryItem,
        ExportValueHistoryItem,
        ImpactHistoryItem,
        ImportMarketSizeHistoryItem,
        ValueToEconomyHistoryItem,
    )
    class_lookup = {}
