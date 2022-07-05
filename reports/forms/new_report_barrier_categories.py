from django import forms


class NewReportBarrierCategoriesForm(forms.Form):
    pass


class NewReportBarrierCategoriesAddForm(forms.Form):
    category = forms.ChoiceField(
        label="",
        choices=[],
        error_messages={"required": "Select a category"},
    )

    def __init__(self, categories, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].choices = [
            (category["id"], category["title"]) for category in categories
        ]
