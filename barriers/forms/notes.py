from django import forms
from django.conf import settings

from .mixins import DocumentMixin

from utils.api.client import MarketAccessAPIClient
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
        content_types=["text/csv", "image/jpeg"],
        max_upload_size=settings.FILE_MAX_SIZE,
        required=False,
    )

    def __init__(self, barrier_id, *args, **kwargs):
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)

    def clean_document(self):
        return self.validate_document()

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.notes.create(
            barrier_id=self.barrier_id,
            text=self.cleaned_data["note"],
            documents=self.cleaned_data.get("document_ids"),
        )


class EditNoteForm(DocumentMixin, forms.Form):
    note = forms.CharField(widget=forms.Textarea)
    document_ids = MultipleValueField(required=False)
    document = RestrictedFileField(
        label="Attach a document",
        content_types=["text/csv", "image/jpeg"],
        max_upload_size=settings.FILE_MAX_SIZE,
        required=False,
    )

    def __init__(self, barrier_id, note_id, *args, **kwargs):
        self.barrier_id = barrier_id
        self.note_id = note_id
        super().__init__(*args, **kwargs)

    def clean_document(self):
        return self.validate_document()

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.notes.update(
            id=self.note_id,
            text=self.cleaned_data["note"],
            documents=self.cleaned_data.get("document_ids"),
        )


class NoteDocumentForm(DocumentMixin, forms.Form):
    document = RestrictedFileField(
        content_types=["text/csv", "image/jpeg"],
        max_upload_size=settings.FILE_MAX_SIZE,
    )

    def save(self):
        return self.upload_document()
