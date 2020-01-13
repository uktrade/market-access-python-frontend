from django import forms


class SaveWatchlistForm(forms.Form):
    REPLACE = "replace"
    NEW = "new"
    CHOICES = [
        (REPLACE, "<strong>Replace</strong> current watch list"),
        (NEW, "<strong>Create new</strong> watch list"),
    ]
    name = forms.CharField(label="Name your watch list ")
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
            (str(index), watchlist.get('name'))
            for index, watchlist in enumerate(watchlists)
        ]

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('replace_or_new') == self.REPLACE:
            if not cleaned_data['replace_index']:
                self.add_error(
                    "replace_index",
                    "Select which watch list to replace"
                )

    def save(self):
        new_watchlist = {
            'name': self.cleaned_data['name'],
            'filters': self.filters,
        }

        if self.cleaned_data['replace_or_new'] == self.NEW:
            self.watchlists.append(new_watchlist)
        elif self.cleaned_data['replace_or_new'] == self.REPLACE:
            index = int(self.cleaned_data['replace_index'])
            self.watchlists = self.watchlists[:index] + [
                new_watchlist
            ] + self.watchlists[index+1:]

        return self.watchlists
