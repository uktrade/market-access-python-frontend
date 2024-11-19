import json

from django import forms


class UserEditBaseForm(forms.Form):

    def clean(self):
        cleaned_data = super().clean()
        cleaned_list = []
        if cleaned_data["form"]:
            cleaned_list = json.loads(cleaned_data["form"])
        if isinstance(cleaned_list, list):
            cleaned_data["form"] = cleaned_list
        else:
            cleaned_data["form"] = [cleaned_list]


class UserEditPolicyTeamsForm(UserEditBaseForm):
    form = forms.CharField(
        required=False,
        label="Policy teams",
        help_text="Add policy teams to keep track on the policy areas which affect the barriers you’ve working on, "
        "or to stay connected with colleagues you work with or manage. ",
    )


class UserEditSectorsForm(UserEditBaseForm):
    form = forms.CharField(
        required=False,
        label="Sectors",
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
    )


class UserEditGovernmentDepartmentForm(UserEditBaseForm):
    form = forms.ChoiceField(
        required=False,
        label="Government department",
        help_text="Add Government departments to stay connected with colleagues outside of the Department of "
        "Business and Trade, who are working on the barriers you’re trying to resolve.",
    )

    def __init__(self, select_options, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["form"].choices = select_options
