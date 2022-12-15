from django import forms


class ChooseUpdateTypeForm(forms.Form):
    update_type = forms.ChoiceField(
        choices=(
            ("top_100_priority", "Top 100 priority barrier"),
            ("programme_fund", "Programme Fund"),
        ),
        error_messages={
            "required": "Select top 100 priority barrier or Programme Fund",
        },
        widget=forms.RadioSelect(attrs={"class": "govuk-radios__input"}),
        label="What is your progress update for?",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
