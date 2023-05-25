from django import forms

from barriers.forms.mixins import APIFormMixin
from utils.forms import (  # MultipleChoiceFieldWithHelpText,; YesNoBooleanField,
    MonthYearField,
)


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
    barrier_summary = forms.CharField(
        label="Public barrier summary",
        help_text=(
            """
            Describe the barrier in a way that is suitable for the public to read
            on GOV.UK. The summary will only be published once it has been
            reviewed internally.
            """
        ),
        error_messages={"required": "Enter a public barrier summary"},
    )
    is_not_published_to_public = forms.ChoiceField(
        label="This barrier should not be published on GOV.UK",
        widget=forms.RadioSelect,
        choices=(
            ("YES", "Yes"),
            ("NO", "No"),
        ),
    )
    # This field needs to be conditionally required - error if empty and
    # 'is_not_published_to_public' is ticked
    is_not_published_reason = forms.CharField(
        label="Explain why the barrier should not be published on GOV.UK",
        help_text=(
            """
            Describe the barrier in a way that is suitable for the public to read
            on GOV.UK. The summary will only be published once it has been
            reviewed internally.
            """
        ),
        error_messages={"required": "Enter why this barrier should not be public"},
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": 5,
            },
        ),
        required=False,
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
        choices={
            ("OPEN", "Open"),
            ("RESOLVED_IN_PART", "Resolved: In part"),
            ("RESOLVED_IN_FULL", "Resolved: In full"),
        },
        widget=forms.RadioSelect,
    )
    start_date = MonthYearField(
        label="When did or will the barrier start to affect trade?",
        help_text="If you aren't sure of the date, give an estimate",
    )
    currently_active = forms.ChoiceField(
        label="Is this barrier currently affecting trade?",
        choices={
            ("YES", "Yes"),
            ("NO", "No, not yet"),
        },
        widget=forms.RadioSelect,
    )


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
