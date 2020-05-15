from django import forms

from utils.api.client import MarketAccessAPIClient


class BaseSavedSearchForm(forms.Form):
    name = forms.CharField(
        label="Saved search name",
        max_length=50,
        error_messages={
            "required": "Enter a name for this search",
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
            raise forms.ValidationError(
                "Search name already in use - please use another name"
            )
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


class SavedSearchNotificationsForm(forms.Form):
    notify_about_additions = forms.BooleanField(
        label="Notify me when a new or existing barrier meets the search criteria",
        required=False,
    )
    notify_about_updates = forms.BooleanField(
        label="Notify me when a barrier that meets the search criteria is updated",
        required=False,
    )

    def __init__(self, token, saved_search_id, *args, **kwargs):
        self.token = token
        self.saved_search_id = saved_search_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        return client.saved_searches.patch(
            id=self.saved_search_id,
            notify_about_additions=self.cleaned_data["notify_about_additions"],
            notify_about_updates=self.cleaned_data["notify_about_updates"],
        )
