from django import forms

from .mixins import APIFormMixin

from utils.api_client import MarketAccessAPIClient


class AddNoteForm(APIFormMixin, forms.Form):
    text = forms.CharField(
        label=(
            'Add notes on an interaction or event'
        ),
        widget=forms.Textarea,
    )

    def save(self):
        client = MarketAccessAPIClient()
        client.notes.create(
            barrier_id=self.id,
            text=self.cleaned_data['text']
        )


class EditNoteForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)

    def __init__(self, barrier_id, note_id, *args, **kwargs):
        self.barrier_id = barrier_id
        self.note_id = note_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient()
        client.notes.update(
            id=self.note_id,
            text=self.cleaned_data['text']
        )
