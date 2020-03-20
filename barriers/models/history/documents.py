from .base import BaseHistoryItem


class BaseDocumentsHistoryItem(BaseHistoryItem):
    field = "documents"
    field_name = "Documents"

    def deleted_documents(self):
        new_documents = {v['id']: v for v in self.new_value}
        old_documents = {v['id']: v for v in self.old_value}
        deleted_ids = set(old_documents.keys()).difference(set(new_documents.keys()))
        return [old_documents[document_id] for document_id in deleted_ids]

    def added_documents(self):
        new_documents = {v['id']:v for v in self.new_value}
        old_documents = {v['id']:v for v in self.old_value}
        added_ids = set(new_documents.keys()).difference(set(old_documents.keys()))
        return [new_documents[document_id] for document_id in added_ids]

    def unchanged_documents(self):
        new_documents = {v['id']:v for v in self.new_value}
        old_documents = {v['id']:v for v in self.old_value}
        unchanged_ids = set(new_documents.keys()).intersection(set(old_documents.keys()))
        return [new_documents[document_id] for document_id in unchanged_ids]
