from django import forms


class ChooseUpdateTypeForm(forms.Form):
    update_type = forms.ChoiceField(
        choices=(
            ("top_100_priority", "Top 100 Priority Barriers"),
            ("programme_fund", "Programme Fund"),
        ),
        error_messages={
            "required": "You must select a project",
        },
        widget=forms.RadioSelect(attrs={"class": "govuk-radios__input"}),
        label="Which project would you like to provide an update for?",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
