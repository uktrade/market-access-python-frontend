from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms

from reports.model_forms.base import NewReportBaseForm

if TYPE_CHECKING:
    from reports.models import Report


class BarrierSource:
    """
    Source as in:
     - Where did you hear about the barrier?
     - Who told you about it?
    """

    COMPANY = "COMPANY"
    TRADE = "TRADE"
    GOVT = "GOVT"
    OTHER = "OTHER"

    @classmethod
    def choices(cls):
        return (
            (cls.COMPANY, "Company"),
            (cls.TRADE, "Trade association"),
            (cls.GOVT, "Government entity"),
            (cls.OTHER, "Other"),
        )


class RelatedToBrexit:
    YES = 1
    NO = 2
    DONT_KNOW = 3

    @classmethod
    def choices(cls):
        return (
            (cls.YES, "Yes"),
            (cls.NO, "No"),
            (cls.DONT_KNOW, "Don't know"),
        )


class NewReportBarrierAboutForm(NewReportBaseForm):
    BS = BarrierSource()
    title = forms.CharField(
        label="Name this barrier",
        help_text=(
            "Include the name of the product, "
            "service or investment and the type of problem. "
            "For example, Import quotas for steel rods."
        ),
        max_length=255,
        error_messages={
            "max_length": "Name should be %(limit_value)d characters or fewer",
            "required": "Enter a name for this barrier",
        },
    )
    product = forms.CharField(
        label="What product, service or investment is affected?",
        max_length=255,
        error_messages={
            "max_length": (
                "Product, service or investment should be %(limit_value)d characters or"
                " fewer"
            ),
            "required": "Enter a product, service or investment",
        },
    )
    source = forms.ChoiceField(
        label="Who told you about the barrier?",
        choices=BS.choices(),
        error_messages={"required": "Select how you became aware of the barrier"},
    )
    other_source = forms.CharField(
        label="Please specify",
        required=False,
        max_length=255,
        error_messages={
            "required": "Select how you became aware of the barrier",
            "max_length": "Other source should be %(limit_value)d characters or fewer",
        },
    )

    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get("source")
        if source == self.BS.OTHER:
            other_source = cleaned_data.get("other_source")
            if not other_source:
                self.add_error("other_source", "This field is required")
        return cleaned_data

    @staticmethod
    def get_barrier_initial(barrier: Report):
        initial_tags = [tag["id"] for tag in barrier.tags]
        return {
            "title": barrier.title,
            "product": barrier.product,
            "source": barrier.source["code"] if barrier.source else None,
            "other_source": barrier.other_source,
        }
