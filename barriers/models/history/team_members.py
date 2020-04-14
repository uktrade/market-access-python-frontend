from .base import BaseHistoryItem, GenericHistoryItem
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
    subclasses = (UserHistoryItem,)
    default_subclass = GenericHistoryItem
    class_lookup = {}
