from django import forms

from utils.api.client import MarketAccessAPIClient


class BaseSavedSearchForm(forms.Form):
    name = forms.CharField(
        label="Name",
        max_length=25,
        error_messages={
            "required": "Enter a name for your saved search",
            "max_length": "Name should be %(limit_value)d characters or fewer",
        },
    )

    def __init__(self, token, *args, **kwargs):
        self.token = token
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data["name"]
        client = MarketAccessAPIClient(self.token)
        saved_searches = client.saved_searches.list(name=name)
        if saved_searches:
            raise forms.ValidationError("Name already in use. Choose a new name.")
        return name


class NewSavedSearchForm(BaseSavedSearchForm):
    def __init__(self, filters, *args, **kwargs):
        self.filters = filters
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        return client.saved_searches.create(
            name=self.cleaned_data["name"],
            filters=self.filters,
        )


class RenameSavedSearchForm(BaseSavedSearchForm):
    def __init__(self, saved_search_id, *args, **kwargs):
        self.saved_search_id = saved_search_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        return client.saved_searches.patch(
            id=self.saved_search_id,
            name=self.cleaned_data["name"],
        )
