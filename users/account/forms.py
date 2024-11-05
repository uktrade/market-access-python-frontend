import json

from django import forms


class UserEditBaseForm(forms.Form):

    def __init__(self, user_id, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.user_id = user_id
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_list = []
        if cleaned_data["form"]:
            cleaned_list = json.loads(cleaned_data["form"])
        cleaned_data["form"] = cleaned_list


class UserEditPolicyTeamsForm(UserEditBaseForm):
    form = forms.CharField(
        required=False,
        label="Policy teams",
        help_text="Help text",
    )


class UserEditSectorsForm(UserEditBaseForm):
    form = forms.CharField(
        required=False,
        label="Sectors",
        help_text="Help text",
    )


class UserEditBarrierLocationsForm(UserEditBaseForm):
    form = forms.CharField(
        required=False,
        label="Barrier locations",
        help_text="All the barrier locations you're interested in by selecting them from the dropdown list. "
        "Or type the first few letters of the location name into the box.",
    )


class UserEditOverseasRegionsForm(UserEditBaseForm):
    form = forms.CharField(
        required=False,
        label="Overseas regions",
        help_text="Help text",
    )


class UserEditGovernmentDepartmentForm(forms.Form):
    # TODO refactor - can it use the base form?
    government_departments = forms.ChoiceField(
        required=False,
        label="Government department",
        help_text="Help text",
    )

    label = "Government department"
    help_text = "Help text"

    def __init__(self, user_id, token, government_departments, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["government_departments"].choices = government_departments

    def clean(self):
        cleaned_data = super().clean()
        cleaned_government_departments = []
        if cleaned_data["government_departments"]:
            cleaned_government_departments = [
                json.loads(cleaned_data["government_departments"])
            ]
        cleaned_data["government_departments"] = cleaned_government_departments
