from django import forms
from django.conf import settings

from .mixins import DocumentMixin

from utils.api_client import MarketAccessAPIClient
from utils.exceptions import FileUploadError, ScanError
from utils.forms import MultipleValueField, RestrictedFileField


class AddNoteForm(DocumentMixin, forms.Form):
    note = forms.CharField(
        label=(
            'Add notes on an interaction or event'
        ),
        widget=forms.Textarea,
    )
    document_ids = MultipleValueField(required=False)
    document = RestrictedFileField(
        label="Attach a document",
        content_types=['text/csv', 'image/jpeg'],
        max_upload_size=settings.FILE_MAX_SIZE,
        required=False,
    )

    def __init__(self, barrier_id, *args, **kwargs):
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)

    def clean_document(self):
        document = self.cleaned_data['document']
        if document:
            try:
                uploaded_document = self.upload_document()
                self.cleaned_data['document_ids'].append(
                    uploaded_document['id']
                )
            except FileUploadError as e:
                self.add_error("document", str(e))
            except ScanError as e:
                self.add_error("document", str(e))
        return document

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.notes.create(
            barrier_id=self.barrier_id,
            text=self.cleaned_data['note'],
            documents=self.cleaned_data.get('document_ids'),
        )


class EditNoteForm(DocumentMixin, forms.Form):
    note = forms.CharField(widget=forms.Textarea)
    document_ids = MultipleValueField(required=False)
    document = RestrictedFileField(
        label="Attach a document",
        content_types=['text/csv', 'image/jpeg'],
        max_upload_size=settings.FILE_MAX_SIZE,
        required=False,
    )

    def __init__(self, barrier_id, note_id, *args, **kwargs):
        self.barrier_id = barrier_id
        self.note_id = note_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)

        document_ids = self.cleaned_data.get('document_ids')

        if self.cleaned_data.get('document'):
            document = self.upload_document()
            document_ids.append(document['id'])

        client.notes.update(
            id=self.note_id,
            text=self.cleaned_data['note'],
            documents=document_ids,
        )


class NoteDocumentForm(DocumentMixin, forms.Form):
    document = RestrictedFileField(
        content_types=['text/csv', 'image/jpeg'],
        max_upload_size=settings.FILE_MAX_SIZE,
    )

    def save(self):
        return self.upload_document()
