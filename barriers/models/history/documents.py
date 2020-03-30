from .base import BaseHistoryItem


class BaseDocumentsHistoryItem(BaseHistoryItem):
    field = "documents"
    field_name = "Documents"

    @property
    def new_document_ids(self):
        return set([document["id"] for document in self.new_value])

    @property
    def old_document_ids(self):
        return set([document["id"] for document in self.old_value])

    @property
    def deleted_documents(self):
        deleted_ids = self.old_document_ids.difference(self.new_document_ids)
        return [
            document for document in self.old_value if document["id"] in deleted_ids
        ]

    @property
    def added_documents(self):
        added_ids = self.new_document_ids.difference(self.old_document_ids)
        return [document for document in self.new_value if document["id"] in added_ids]

    @property
    def unchanged_documents(self):
        unchanged_ids = self.new_document_ids.intersection(self.old_document_ids)
        return [
            document for document in self.new_value if document["id"] in unchanged_ids
        ]
