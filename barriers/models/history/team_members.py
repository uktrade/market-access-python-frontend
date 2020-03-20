from .base import BaseHistoryItem
from .utils import PolymorphicBase


class UserHistoryItem(BaseHistoryItem):
    field = "user"
    field_name = "Barrier team"


class TeamMemberHistoryItem(PolymorphicBase):
    """
    Polymorphic wrapper for HistoryItem classes
    """

    model = "team_member"
    key = "field"
    subclasses = (
        UserHistoryItem,
    )
    class_lookup = {}
