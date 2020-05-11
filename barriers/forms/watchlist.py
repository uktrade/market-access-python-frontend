from django import forms
from django.conf import settings

from .mixins import APIFormMixin

from ..models import Watchlist

from utils.api.client import MarketAccessAPIClient


class NewSavedSearchForm(forms.Form):
    name = forms.CharField(
        label="Name",
        max_length=settings.MAX_WATCHLIST_NAME_LENGTH,
        error_messages={"required": "Enter a name for your saved search"},
    )

    def __init__(self, token, filters, *args, **kwargs):
        self.token = token
        self.filters = filters
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        return client.saved_searches.create(
            name=self.cleaned_data["name"],
            filters=self.filters,
        )


class RenameSavedSearchForm(forms.Form):
    name = forms.CharField(
        label="New name",
        max_length=settings.MAX_WATCHLIST_NAME_LENGTH,
        error_messages={
            "required": "Enter a name for your watch list",
            "max_length": "Name should be %(limit_value)d characters or fewer",
        },
    )


class EditWatchlistForm(forms.Form):
    name = forms.CharField(
        label="Name your watch list",
        max_length=settings.MAX_WATCHLIST_NAME_LENGTH,
        error_messages={"required": "Enter a name for your watch list"},
    )
