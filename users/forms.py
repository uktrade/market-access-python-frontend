from django import forms

from barriers.forms.mixins import APIFormMixin
from utils.api.client import MarketAccessAPIClient


class UserSearchForm(forms.Form):
    query = forms.CharField(
        label="Find a user to add",
        max_length=255,
        required=False,
    )


class UserGroupForm(APIFormMixin, forms.Form):
    group = forms.ChoiceField(
        label="Role",
        choices=[("0", "General user")],
        error_messages={"required": "Select a role"},
    )

    def __init__(self, groups, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["group"].choices += (
            (str(group.id), group.name) for group in groups
        )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.cleaned_data.get("group") == "0":
            groups = []
        else:
            groups = [{"id": self.cleaned_data["group"]}]
        client.users.patch(id=self.id, groups=groups)
