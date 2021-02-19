from django import forms
from django.conf import settings

from utils.api.client import MarketAccessAPIClient
from utils.forms import MultipleValueField, RestrictedFileField

from .mixins import DocumentMixin


class AddNoteForm(DocumentMixin, forms.Form):
    note = forms.CharField(
        label=("Add notes on an interaction or event"),
        widget=forms.Textarea,
        error_messages={"required": "Add text for the note."},
    )
    document_ids = MultipleValueField(required=False)
    document = RestrictedFileField(
        label="Attach a document",
        content_types=settings.ALLOWED_FILE_TYPES,
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


class AddPublicBarrierNoteForm(forms.Form):
    note = forms.CharField(
        label=(
            "Is something incorrect or out of date? Enter the details so an Editor can "
            "update the barrier."
        ),
        widget=forms.Textarea,
        error_messages={"required": "Add text for the note."},
    )

    def __init__(self, token, barrier_id, *args, **kwargs):
        self.token = token
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.public_barriers.create_note(
            id=self.barrier_id,
            text=self.cleaned_data["note"],
        )


class EditNoteForm(DocumentMixin, forms.Form):
    note = forms.CharField(
        widget=forms.Textarea,
        error_messages={"required": "Add text for the note."},
    )
    document_ids = MultipleValueField(required=False)
    document = RestrictedFileField(
        label="Attach a document",
        content_types=settings.ALLOWED_FILE_TYPES,
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


class EditPublicBarrierNoteForm(forms.Form):
    note = forms.CharField(
        label=(
            "Is something incorrect or out of date? Enter the details so an Editor can "
            "update the barrier."
        ),
        widget=forms.Textarea,
        error_messages={"required": "Add text for the note."},
    )

    def __init__(self, token, note_id, *args, **kwargs):
        self.token = token
        self.note_id = note_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.public_barrier_notes.patch(
            id=self.note_id,
            text=self.cleaned_data["note"],
        )


class NoteDocumentForm(DocumentMixin, forms.Form):
    document = RestrictedFileField(
        content_types=settings.ALLOWED_FILE_TYPES,
        max_upload_size=settings.FILE_MAX_SIZE,
    )

    def save(self):
        return self.upload_document()
