from django import forms


class UserSearchForm(forms.Form):
    query = forms.CharField(
        label="Find a user to add as a contributor",
        max_length=255,
        required=False,
    )
