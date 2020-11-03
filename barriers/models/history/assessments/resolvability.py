from ..base import BaseHistoryItem, GenericHistoryItem
from ..utils import PolymorphicBase


class ApprovedHistoryItem(BaseHistoryItem):
    field = "approved"
    field_name = "Resolvability assessment: Approval"

    def get_value(self, value):
        if value is True:
            return "Approved"
        elif value is False:
            return "Rejected"


class ArchivedHistoryItem(BaseHistoryItem):
    field = "archived"
    field_name = "Resolvability assessment: Archived"

    def get_value(self, value):
        if value is True:
            return "Archived"
        elif value is False:
            return "Unarchived"


class EffortToResolveHistoryItem(BaseHistoryItem):
    field = "effort_to_resolve"
    field_name = "Resolvability assessment: Effort to resolve"

    def get_value(self, value):
        if value:
            return value.get("name")


class ExplanationHistoryItem(BaseHistoryItem):
    field = "explanation"
    field_name = "Resolvability assessment: Explanation"


class TimeToResolveHistoryItem(BaseHistoryItem):
    field = "time_to_resolve"
    field_name = "Resolvability assessment: Time to resolve"

    def get_value(self, value):
        if value:
            return value.get("name")


class ResolvabilityAssessmentHistoryItem(PolymorphicBase):
    model = "resolvability_assessment"
    key = "field"
    subclasses = (
        ArchivedHistoryItem,
        ApprovedHistoryItem,
        EffortToResolveHistoryItem,
        ExplanationHistoryItem,
        TimeToResolveHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}
