from django import forms
from django.conf import settings

from .mixins import CustomErrorsMixin

from ..models import Watchlist


class SaveWatchlistForm(CustomErrorsMixin, forms.Form):
    REPLACE = "replace"
    NEW = "new"
    CHOICES = [
        (REPLACE, "<strong>Replace</strong> current watch list"),
        (NEW, "<strong>Create new</strong> watch list"),
    ]
    name = forms.CharField(
        label="Name your watch list",
        max_length=settings.MAX_WATCHLIST_NAME_LENGTH,
    )
    replace_or_new = forms.ChoiceField(
        label="Replace current list or create new?",
        choices=CHOICES,
        widget=forms.RadioSelect,
    )
    replace_index = forms.ChoiceField(
        label="Which list would you like to replace?",
        required=False,
    )

    def __init__(self, watchlists, filters, *args, **kwargs):
        self.watchlists = watchlists
        self.filters = filters
        super().__init__(*args, **kwargs)
        self.fields['replace_index'].choices = [
            (str(index), watchlist.name)
            for index, watchlist in enumerate(watchlists)
        ]
        if self.has_to_replace():
            del self.fields['replace_or_new']
            self.fields['replace_index'].required = True
        elif self.has_to_create():
            del self.fields['replace_or_new']

    def has_to_create(self):
        return len(self.watchlists) == 0

    def has_to_replace(self):
        return len(self.watchlists) >= settings.MAX_WATCHLIST_LENGTH

    def get_new_watchlist_index(self):
        replace_index = self.cleaned_data.get('replace_index')
        if replace_index not in self.fields['replace_index'].empty_values:
            return int(replace_index)
        return len(self.watchlists) - 1

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('replace_or_new') == self.REPLACE:
            if not cleaned_data['replace_index']:
                self.add_error(
                    "replace_index",
                    "Select which watch list to replace"
                )

    def save(self):
        new_watchlist = Watchlist(
            name=self.cleaned_data['name'],
            filters=self.filters,
        )

        replace_or_new = self.cleaned_data.get('replace_or_new')

        if self.has_to_create() or replace_or_new == self.NEW:
            self.watchlists.append(new_watchlist)
        elif self.has_to_replace() or replace_or_new == self.REPLACE:
            index = int(self.cleaned_data['replace_index'])
            self.watchlists = self.watchlists[:index] + [
                new_watchlist
            ] + self.watchlists[index+1:]

        return self.watchlists


class RenameWatchlistForm(CustomErrorsMixin, forms.Form):
    name = forms.CharField(
        label="Name your watch list",
        max_length=settings.MAX_WATCHLIST_NAME_LENGTH,
    )


class EditWatchlistForm(CustomErrorsMixin, forms.Form):
    name = forms.CharField(
        label="Name your watch list",
        max_length=settings.MAX_WATCHLIST_NAME_LENGTH,
    )
