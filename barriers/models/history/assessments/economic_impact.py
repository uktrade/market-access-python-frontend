from ..base import BaseHistoryItem, GenericHistoryItem
from ..utils import PolymorphicBase


class ArchivedHistoryItem(BaseHistoryItem):
    field = "archived"
    field_name = "Economic impact assessment: Archived"

    def get_value(self, value):
        if value is True:
            return "Archived"
        elif value is False:
            return "Unarchived"


class ExplanationHistoryItem(BaseHistoryItem):
    field = "explanation"
    field_name = "Economic impact assessment: Explanation"


class ImpactHistoryItem(BaseHistoryItem):
    field = "impact"
    field_name = "Economic impact assessment: Impact"

    def get_value(self, value):
        if value:
            return value.get("name")


class EconomicImpactAssessmentHistoryItem(PolymorphicBase):
    model = "economic_impact_assessment"
    key = "field"
    subclasses = (
        ArchivedHistoryItem,
        ExplanationHistoryItem,
        ImpactHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}
