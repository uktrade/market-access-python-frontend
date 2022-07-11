from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from reports.model_forms.base import NewReportBaseForm
from utils.forms import MultipleChoiceFieldWithHelpText

if TYPE_CHECKING:
    from reports.models import Report


class NewReportBarrierCategoriesForm(NewReportBaseForm):
    categories = forms.CharField(
        required=False,
        error_messages={"required": "Please select at least one category"},
    )

    def clean_categories(self):
        categories = self.cleaned_data["categories"]
        if not categories:
            raise forms.ValidationError("Please select at least one category")
        return categories.split(",")

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        return {
            "categories": [category["id"] for category in barrier.categories],
        }


class NewReportBarrierCategoriesAddForm(NewReportBaseForm):
    category = forms.ChoiceField(
        label="",
        choices=[],
        error_messages={"required": "Select a category"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = self.metadata.get_category_list()
        self.fields["category"].choices = [
            (category["id"], category["title"]) for category in categories
        ]

    @staticmethod
    def get_barrier_initial(barrier: Report) -> dict[str, any]:
        return {}
