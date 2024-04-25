from django import forms
from django.utils.safestring import mark_safe

from utils.forms import fields


class ChooseUpdateTypeForm(forms.Form):
    update_type = forms.ChoiceField(
        choices=(
            (
                "top_100_priority",
                mark_safe(
                    "<span class='govuk-body'>Barrier progress</span> <span class='govuk-hint'>Monthly updates for"
                    " PB100 barriers, including any using the Regulator Fund</span>"
                ),
            ),
            (
                "programme_fund",
                mark_safe(
                    "<span class='govuk-body'>Programme Fund</span> <span class='govuk-hint'>Regular updates on barriers"
                    " using the Facilitative Regional Funds</span>"
                ),
            ),
        ),
        help_text=("a", "b"),
        error_messages={
            "required": "Select barrier progress or Programme Fund",
        },
        widget=forms.RadioSelect(attrs={"class": "govuk-radios__input"}),
        label="What is your progress update for?",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
