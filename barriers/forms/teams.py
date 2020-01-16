from django import forms

from .mixins import CustomErrorsMixin


class UserSearchForm(CustomErrorsMixin, forms.Form):
    query = forms.CharField(label='Find a user', max_length=255)


class AddTeamMemberForm(CustomErrorsMixin, forms.Form):
    user = forms.CharField(
        label='Name',
        max_length=255,
        widget=forms.HiddenInput(),
    )
    role = forms.CharField(label='Role', max_length=255)
