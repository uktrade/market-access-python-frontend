import logging

from django import forms
from django.conf import settings

from barriers.forms.mixins import APIFormMixin
from users.constants import (
    REGIONAL_LEAD_PERMISSION_GROUPS,
    USER_ADDITIONAL_PERMISSION_GROUPS,
)
from utils.api.client import MarketAccessAPIClient

logger = logging.getLogger(__name__)


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
    additional_permissions = forms.MultipleChoiceField(
        label="Permissions",
        choices=[],
        required=False,
    )
    regional_lead_groups = forms.MultipleChoiceField(
        label="Regional Leader Assignment",
        choices=[],
        required=False,
    )

    def __init__(self, groups, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 2 Types of group in the groups list; roles and additional permissions
        # users should only have one role, but can belong to multiple addition permission groups.
        # Add group to the radio button group select if it is a 'role'
        # Add group to the checkbox group select if it is an 'additional permission'
        # Regional Leader permission groups are seperated so only admins can assign users

        for group in groups:
            if group.name == "Role administrator":
                if settings.DISPLAY_ROLE_ADMIN_GROUP:
                    self.fields["additional_permissions"].choices.append(
                        (str(group.id), group.name)
                    )
            elif group.name in USER_ADDITIONAL_PERMISSION_GROUPS:
                self.fields["additional_permissions"].choices.append(
                    (str(group.id), group.name)
                )
            elif group.name in REGIONAL_LEAD_PERMISSION_GROUPS:
                self.fields["regional_lead_groups"].choices.append(
                    (str(group.id), group.name)
                )
            else:
                self.fields["group"].choices.append((str(group.id), group.name))

    def save(self):
        client = MarketAccessAPIClient(self.token)

        # Groups/roles list
        if self.cleaned_data.get("group") == "0":
            groups = []
        else:
            groups = [{"id": self.cleaned_data["group"]}]

        # Additional permissions
        selected_permissions = self.cleaned_data.get("additional_permissions")
        for added_permission in selected_permissions:
            groups.append({"id": added_permission})

        # Regional leader assignment
        regions_selected = self.cleaned_data.get("regional_lead_groups")
        for region_lead_permission in regions_selected:
            groups.append({"id": region_lead_permission})

        client.users.patch(id=self.id, groups=groups)


class UserDeleteForm(APIFormMixin, forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_to_delete = kwargs["id"]

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.users.patch(id=self.id_to_delete, is_active=False, groups=[])
