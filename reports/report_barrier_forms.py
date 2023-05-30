import logging

from django import forms

from barriers.constants import REPORTABLE_STATUSES, REPORTABLE_STATUSES_HELP_TEXT
from barriers.forms.mixins import APIFormMixin
from utils.forms import MonthYearField

logger = logging.getLogger(__name__)


class BarrierAboutForm(APIFormMixin, forms.Form):
    barrier_title = forms.CharField(
        label="Barrier title",
        help_text=(
            """
            The title should be suitable for the public to read on GOV.UK.
            It will only be published once it has been reviewed internally.
            Include the product, service or investment and the type of problem.
            For example, Import quotas for steel rods.
            """
        ),
        max_length=150,
        error_messages={
            "max_length": "Name should be %(limit_value)d characters or less",
            "required": "Enter a barrier title",
        },
        widget=forms.Textarea(
            attrs={
                "class": "govuk-input",
                "rows": 10,
            },
        ),
    )

    barrier_description = forms.CharField(
        label="Barrier description",
        help_text=(
            """
        This description will only be used internally.
        Explain how the barrier is affecting trade,
        and why it exists. Where relevant include the specific laws
        or measures blocking trade,
        and any political context.
        """
        ),
        error_messages={"required": "Enter a barrier description"},
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": 5,
            },
        ),
        initial="",
    )

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


class BarrierStatusForm(APIFormMixin, forms.Form):
    barrier_status = forms.ChoiceField(
        label="Choose barrier status",
        choices=REPORTABLE_STATUSES,
        help_text=REPORTABLE_STATUSES_HELP_TEXT,
        widget=forms.RadioSelect,
        error_messages={"required": "Select barrier status"},
    )
    # will need bespoke error catching in the clean method for these resolved fields
    partially_resolved_date = MonthYearField(
        label="Date the barrier was partially resolved",
        required=False,
        error_messages={
            "invalid_year": "Enter a valid date",
            "invalid_month": "Enter a valid date",
        },
    )
    partially_resolved_description = forms.CharField(
        label="Describe briefly how this barrier was partially resolved",
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": 5,
            },
        ),
        required=False,
        initial="",
    )
    resolved_date = MonthYearField(
        label="Date the barrier was resolved",
        required=False,
        error_messages={
            "invalid_year": "Enter a valid date",
            "invalid_month": "Enter a valid date",
        },
    )
    resolved_description = forms.CharField(
        label="Describe briefly how this barrier was resolved",
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": 5,
            },
        ),
        required=False,
        initial="",
    )
    start_date_known = forms.BooleanField(
        label="I don't know",
        required=False,
    )
    start_date = MonthYearField(
        label="When did or will the barrier start to affect trade?",
        help_text="If you aren't sure of the date, give an estimate",
        error_messages={"required": "Enter a date"},
        required=False,
    )
    currently_active = forms.ChoiceField(
        label="Is this barrier currently affecting trade?",
        choices=(
            ("YES", "Yes"),
            ("NO", "No, not yet"),
        ),
        widget=forms.RadioSelect(attrs={"class": "govuk-radios__input"}),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("barrier_status")
        partially_resolved_date = cleaned_data.get("partially_resolved_date")
        partially_resolved_description = cleaned_data.get(
            "partially_resolved_description"
        )
        resolved_date = cleaned_data.get("resolved_date")
        resolved_description = cleaned_data.get("resolved_description")
        start_date_known = cleaned_data.get("start_date_known")
        start_date = cleaned_data.get("start_date")
        currently_active = cleaned_data.get("currently_active")

        if status == "3":
            # Partially resolved date and reason requried
            if partially_resolved_date is None:
                msg = "Enter a date the barrier was partially resolved"
                self.add_error("partially_resolved_date", msg)
            if partially_resolved_description == "":
                msg = "Enter a description for partially resolved"
                self.add_error("partially_resolved_description", msg)

        if status == "4":
            # Resolved date and reason requried
            if resolved_date is None:
                msg = "Enter a date the barrier was resolved"
                self.add_error("resolved_date", msg)
            if resolved_description == "":
                msg = "Enter a description for resolved"
                self.add_error("resolved_description", msg)

        if start_date is None and start_date_known is False:
            msg = "Enter a date the barrier started to affect trade or I don't know"
            self.add_error("start_date", msg)

        if start_date_known and currently_active == "":
            msg = "Is the barrier affecting trade"
            self.add_error("currently_active", msg)


class BarrierLocationForm(APIFormMixin, forms.Form):
    # TODO get the existing location search stuff into this page
    location = forms.CharField(
        label="Which location does the barrier relate to?",
        help_text=(
            """
            Select a trading bloc if the barrier applies to the whole
            trading bloc. Select a country if the barrier is a trading
            bloc regulation that only applies to that country.
            """
        ),
    )


class BarrierTradeDirectionForm(APIFormMixin, forms.Form):
    trade_direction = forms.ChoiceField(
        label="Which trade direction does this barrier affect?",
        choices={
            ("EXPORTING", "Exporting from th UK or investing overseas"),
            ("IMPORTING", "Importing or investing into the UK"),
        },
        widget=forms.RadioSelect,
    )


class BarrierSectorsAffectedForm(APIFormMixin, forms.Form):
    # TODO get the existing sectors selectors stuff into this page
    main_sectors_affected = forms.CharField(
        label="Main sector affected",
        help_text=("Add the sector you think the barrier affects the most"),
    )
    other_sectors_affected = forms.CharField(
        label="Other sectors (optional)",
        help_text=("Add all the other sectors affected by the barrier"),
    )


class BarrierCompaniesAffectedForm(APIFormMixin, forms.Form):
    # TODO get the existing companies search stuff into this page
    companies_affected = forms.CharField(
        label="Name of company affected by the barrier",
        help_text=("You can search by name, address or company number"),
    )


class BarrierExportTypeForm(APIFormMixin, forms.Form):
    export_type = forms.MultipleChoiceField(
        label="Which types of exports does the barrier affect?",
        help_text="Select all that apply",
        choices=(
            ("GOODS", "Goods"),
            ("SERIVCES", "Services"),
            ("INVESTMENTS", "Investments"),
        ),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "govuk-checkboxes__input"}),
        error_messages={
            "required": "You must select one or more affected exports.",
        },
    )
    export_description = forms.CharField(
        label="Which goods, services or investments does the barrier affect?",
        help_text=(
            """
            Enter all goods, services or investments affected.
            Be as specific as you can.
            """
        ),
    )
    # TODO - Somehow get the existing HS code component into this page.
    hs_code_input = forms.CharField(
        label="put the hs code search component here",
        help_text=("tricky stuff!"),
    )
