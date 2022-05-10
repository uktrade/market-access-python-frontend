import logging

from django import forms

from utils.api.client import MarketAccessAPIClient

logger = logging.getLogger(__name__)


class AddCategoryForm(forms.Form):
    category = forms.ChoiceField(
        label="",
        choices=[],
        error_messages={"required": "Select a category"},
    )

    def __init__(self, categories, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].choices = [
            (category["id"], category["title"]) for category in categories
        ]


class EditCategoriesForm(forms.Form):
    categories = forms.MultipleChoiceField(
        label="",
        choices=[],
        widget=forms.MultipleHiddenInput(),
        required=False,
    )

    def __init__(self, barrier_id, categories, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)
        self.fields["categories"].choices = [
            (category["id"], category["title"]) for category in categories
        ]

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.barrier_id,
            categories=self.cleaned_data["categories"],
        )
