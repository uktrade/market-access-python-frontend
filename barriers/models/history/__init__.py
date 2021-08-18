from barriers.models.history.action_plans import (
    ActionPlanHistoryItem, ActionPlanMilestoneHistoryItem,
    ActionPlanTaskHistoryItem)

from .assessments.economic import EconomicAssessmentHistoryItem
from .assessments.economic_impact import EconomicImpactAssessmentHistoryItem
from .assessments.resolvability import ResolvabilityAssessmentHistoryItem
from .assessments.strategic import StrategicAssessmentHistoryItem
from .barriers import BarrierHistoryItem
from .notes import NoteHistoryItem
from .public_barrier_notes import PublicBarrierNoteHistoryItem
from .public_barriers import PublicBarrierHistoryItem
from .team_members import TeamMemberHistoryItem
from .utils import PolymorphicBase
from .wto import WTOHistoryItem


class HistoryItem(PolymorphicBase):
    """
    Polymorphic wrapper for HistoryItem classes

    Delegates to the correct subclass based on the value of data["model"]
    That class then delegates to a subclass based on data["field"]
    """

    key = "model"
    subclasses = (
        BarrierHistoryItem,
        EconomicAssessmentHistoryItem,
        EconomicImpactAssessmentHistoryItem,
        NoteHistoryItem,
        PublicBarrierHistoryItem,
        PublicBarrierNoteHistoryItem,
        ResolvabilityAssessmentHistoryItem,
        StrategicAssessmentHistoryItem,
        TeamMemberHistoryItem,
        WTOHistoryItem,
        ActionPlanHistoryItem,
        ActionPlanMilestoneHistoryItem,
        ActionPlanTaskHistoryItem
    )
    class_lookup = {}
