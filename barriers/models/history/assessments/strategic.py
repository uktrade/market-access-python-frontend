from ..base import BaseHistoryItem, GenericHistoryItem
from ..utils import PolymorphicBase


class ApprovedHistoryItem(BaseHistoryItem):
    field = "approved"
    field_name = "Stretegic assessment: Approval"

    def get_value(self, value):
        if value is True:
            return "Approved"
        elif value is False:
            return "Rejected"


class ArchivedHistoryItem(BaseHistoryItem):
    field = "archived"
    field_name = "Stretegic assessment: Archived"

    def get_value(self, value):
        if value is True:
            return "Archived"
        elif value is False:
            return "Unarchived"


class HMGStrategyHistoryItem(BaseHistoryItem):
    field = "hmg_strategy"
    field_name = "Stretegic assessment: HMG strategy"


class GovernmentPolicyHistoryItem(BaseHistoryItem):
    field = "government_policy"
    field_name = "Stretegic assessment: Government policy"


class TradingRelationsHistoryItem(BaseHistoryItem):
    field = "trading_relations"
    field_name = "Stretegic assessment: Trading relations"


class UKInterestAndSecurityHistoryItem(BaseHistoryItem):
    field = "uk_interest_and_security"
    field_name = "Stretegic assessment: UK interest and security"


class UKGrantsHistoryItem(BaseHistoryItem):
    field = "uk_grants"
    field_name = "Stretegic assessment: UK grants"


class CompetitionHistoryItem(BaseHistoryItem):
    field = "competition"
    field_name = "Stretegic assessment: Competition"


class AdditionalInformationHistoryItem(BaseHistoryItem):
    field = "additional_information"
    field_name = "Stretegic assessment: Additional information"


class ScaleHistoryItem(BaseHistoryItem):
    field = "scale"
    field_name = "Stretegic assessment: Scale"

    def get_value(self, value):
        if value:
            return value.get("name")


class StrategicAssessmentHistoryItem(PolymorphicBase):
    model = "strategic_assessment"
    key = "field"
    subclasses = (
        ApprovedHistoryItem,
        ArchivedHistoryItem,
        HMGStrategyHistoryItem,
        GovernmentPolicyHistoryItem,
        TradingRelationsHistoryItem,
        UKInterestAndSecurityHistoryItem,
        UKGrantsHistoryItem,
        CompetitionHistoryItem,
        AdditionalInformationHistoryItem,
        ScaleHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}
