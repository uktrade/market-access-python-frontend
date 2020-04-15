from .base import BaseHistoryItem, GenericHistoryItem
from .documents import BaseDocumentsHistoryItem
from .utils import PolymorphicBase


class TextHistoryItem(BaseHistoryItem):
    field = "text"
    field_name = "Notes"


class DocumentsHistoryItem(BaseDocumentsHistoryItem):
    field = "documents"
    field_name = "Documents"


class NoteHistoryItem(PolymorphicBase):
    """
    Polymorphic wrapper for HistoryItem classes
    """

    model = "note"
    key = "field"
    subclasses = (
        DocumentsHistoryItem,
        TextHistoryItem,
    )
    default_subclass = GenericHistoryItem
    class_lookup = {}
