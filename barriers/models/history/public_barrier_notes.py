from .base import BaseHistoryItem, GenericHistoryItem
from .utils import PolymorphicBase


class ArchivedHistoryItem(BaseHistoryItem):
    field = "archived"
    field_name = "Public barrier notes"


class TextHistoryItem(BaseHistoryItem):
    field = "text"
    field_name = "Public barrier notes"


class PublicBarrierNoteHistoryItem(PolymorphicBase):
    model = "public_barrier_note"
    key = "field"
    subclasses = (
        ArchivedHistoryItem,
        TextHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}
