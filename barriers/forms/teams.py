from django import forms


class UserSearchForm(forms.Form):
    query = forms.CharField(
        label='Find a user',
        max_length=255,
        required=False,
    )


class AddTeamMemberForm(forms.Form):
    user = forms.CharField(
        label='Name',
        max_length=255,
        widget=forms.HiddenInput(),
    )
    role = forms.CharField(
        label='Role',
        max_length=255,
        error_messages={'required': "Enter a role"},
    )
