from .assessments import AssessmentHistoryItem
from .barriers import BarrierHistoryItem
from .notes import NoteHistoryItem
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
        AssessmentHistoryItem,
        BarrierHistoryItem,
        NoteHistoryItem,
        PublicBarrierHistoryItem,
        TeamMemberHistoryItem,
        WTOHistoryItem,
    )
    class_lookup = {}
