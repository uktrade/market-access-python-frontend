from .base import BaseHistoryItem, GenericHistoryItem
from .utils import PolymorphicBase


class MilestonesAndDeliverablesHistoryItem(BaseHistoryItem):
    field = "milestones_and_deliverables"
    field_name = "Milestones and Deliverables"


class ExpenditureHistoryItem(BaseHistoryItem):
    field = "expenditure"
    field_name = "Expenditure"


class ProgrammeFundsHistoryItem(PolymorphicBase):
    """
    Polymorphic wrapper for HistoryItem classes
    """

    model = "programme_fund_progress_update"
    key = "field"
    subclasses = (
        ExpenditureHistoryItem,
        MilestonesAndDeliverablesHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}
