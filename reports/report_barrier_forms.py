import datetime
import json
import logging

from django import forms

from barriers.constants import (
    EXPORT_TYPES,
    REPORTABLE_STATUSES,
    REPORTABLE_STATUSES_HELP_TEXT,
)
from barriers.forms.mixins import APIFormMixin
from utils.forms import (
    CommodityCodeWidget,
    MonthYearField,
    MonthYearInFutureField,
    MultipleValueField,
)
from utils.metadata import MetadataMixin

logger = logging.getLogger(__name__)


class BarrierAboutForm(APIFormMixin, forms.Form):
    title = forms.CharField(
        label="Barrier title",
        help_text=(
            """
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
                "class": "govuk-input govuk-js-character-count js-character-count",
                "rows": 10,
            },
        ),
    )

    summary = forms.CharField(
        label="Barrier description",
        help_text=(
            """
            Explain how the barrier is affecting trade and why it exists.
            Where relevant include the specific laws or measures blocking trade,
            and any political context.
            """
        ),
        max_length=300,
        error_messages={"required": "Enter a barrier description"},
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea govuk-textarea govuk-js-character-count js-character-count",
                "rows": 5,
            },
        ),
        initial="",
    )


class BarrierStatusForm(APIFormMixin, forms.Form):
    status = forms.ChoiceField(
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
            "invalid_year": "Enter a date in the format 01 2023",
            "invalid_month": "Enter a date in the format 01 2023",
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
            "invalid_year": "Enter a date in the format 01 2023",
            "invalid_month": "Enter a date in the format 01 2023",
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
    start_date_unknown = forms.BooleanField(
        label="I don't know",
        required=False,
    )
    start_date = MonthYearInFutureField(
        label="When did or will the barrier start to affect trade?",
        help_text="If you don’t know the month, enter 06.",
        error_messages={
            "required": "Enter a date",
            "invalid_year": "Enter a date in the format 01 2023",
            "invalid_month": "Enter a date in the format 01 2023",
        },
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
        status = cleaned_data.get("status")
        partially_resolved_date = cleaned_data.get("partially_resolved_date")
        partially_resolved_description = cleaned_data.get(
            "partially_resolved_description"
        )
        resolved_date = cleaned_data.get("resolved_date")
        resolved_description = cleaned_data.get("resolved_description")
        start_date_unknown = cleaned_data.get("start_date_unknown")
        start_date = cleaned_data.get("start_date")
        currently_active = cleaned_data.get("currently_active")

        # Setup keys for status date and summary
        cleaned_data["status_date"] = datetime.date.today()
        cleaned_data["status_summary"] = ""

        if partially_resolved_date and resolved_date:
            msg = "Enter either a date the barrier was partially resolved or a date the barrier was fully resolved"
            self.add_error("partially_resolved_date", msg)
            self.add_error("resolved_date", msg)

        if status == "3":
            # Partially resolved date and reason requried
            if partially_resolved_date is None:
                msg = "Enter a date the barrier was partially resolved"
                self.add_error("partially_resolved_date", msg)
            if partially_resolved_description == "":
                msg = "Enter a description"
                self.add_error("partially_resolved_description", msg)
            cleaned_data["status_date"] = partially_resolved_date
            cleaned_data["status_summary"] = partially_resolved_description

        if status == "4":
            # Resolved date and reason requried
            if resolved_date is None:
                msg = "Enter a date the barrier was resolved"
                self.add_error("resolved_date", msg)
            if resolved_description == "":
                msg = "Enter a description"
                self.add_error("resolved_description", msg)
            cleaned_data["status_date"] = resolved_date
            cleaned_data["status_summary"] = resolved_description

        if (start_date is None and start_date_unknown is False) or (
            start_date and start_date_unknown is True
        ):
            msg = "Enter a date or select 'I don't know'."
            self.add_error("start_date", msg)

        if start_date_unknown and currently_active == "":
            msg = "Select yes if the barrier is currently affecting trade"
            self.add_error("currently_active", msg)

        if start_date:
            cleaned_data["start_date"] = start_date
            cleaned_data["start_date_known"] = True
            # If the given start date is in the past, currently active is true
            if start_date <= datetime.date.today():
                cleaned_data["is_currently_active"] = True
            else:
                cleaned_data["is_currently_active"] = False
        else:
            cleaned_data["start_date"] = None

        if start_date_unknown:
            # 'I don't know' has been checked
            cleaned_data["start_date_known"] = False
            cleaned_data["is_currently_active"] = currently_active

        return cleaned_data


class BarrierLocationForm(APIFormMixin, MetadataMixin, forms.Form):
    location_select = forms.ChoiceField(
        label="Which location does the barrier relate to?",
        error_messages={"required": "Select a location for this barrier"},
        help_text=(
            """
            Select a trading bloc if the barrier relates to the whole trading bloc.
            Select a country if the barrier is a trading bloc regulation that only
            applies to that country.
            """
        ),
        required=True,
    )
    affect_whole_country = forms.BooleanField(
        widget=forms.HiddenInput(),
        required=False,
    )
    admin_areas = forms.CharField(
        label="Which admin area does the barrier relate to?",
        help_text="Select all that apply",
        widget=forms.HiddenInput(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get data we need for options
        self.countries_options = self.metadata.get_country_list()
        self.trading_blocs = self.metadata.get_trading_bloc_list()

        # Set the choices for the country select box
        self.fields["location_select"].choices = (
            (0, "Choose a location"),
            (
                "Trading blocs",
                tuple([(bloc["code"], bloc["name"]) for bloc in self.trading_blocs]),
            ),
            (
                "Countries",
                tuple(
                    (country["id"], country["name"])
                    for country in self.countries_options
                ),
            ),
        )

        # Set dictionary to pass to frontend so JS knows which countries need
        # to see trading bloc sections
        self.trading_bloc_countries = {}

        # Need to dynamically create the trading blocs questions
        for trading_bloc in self.trading_blocs:
            bloc_name = trading_bloc["name"]
            short_bloc_name = trading_bloc["short_name"].split()[1]

            # Add to trading bloc countries dictionary for the JS frontend
            self.trading_bloc_countries[short_bloc_name] = trading_bloc["country_ids"]

            field_name = "trading_bloc_" + short_bloc_name
            self.fields[field_name] = forms.ChoiceField(
                label=f"Was this barrier caused by a regulation introduced by the {short_bloc_name}?",
                help_text=(
                    f"""
                    Yes should be selected if the barrier is a local application
                    of an {short_bloc_name} regulation. If it is an {short_bloc_name}-wide barrier, the
                    country location should be changed to {bloc_name} in the
                    location screen.
                    """
                ),
                choices=(
                    ("YES", "Yes"),
                    ("NO", "No"),
                    ("UNKNOWN", "Don't know"),
                ),
                widget=forms.RadioSelect(attrs={"class": "govuk-radios__input"}),
                required=False,
            )

        # Create lists for selection dropdowns
        countries_with_admin_areas = self.metadata.get_countries_with_admin_areas_list()
        admin_area_choices_dict = {}
        for admin_area_country in countries_with_admin_areas:
            admin_areas = self.metadata.get_admin_areas_by_country(
                admin_area_country["id"]
            )
            country_name = admin_area_country["name"]
            field_name = "admin_areas_" + country_name

            admin_area_choices = [(0, "Choose an admin area")] + [
                (area["id"], area["name"]) for area in admin_areas
            ]
            admin_area_choices_dict[field_name] = admin_area_choices
        self.admin_area_choices = admin_area_choices_dict

    def clean(self):
        cleaned_data = super().clean()

        # Map the location selected to the correct DB field
        location = self.cleaned_data["location_select"]
        selected_admin_areas = self.cleaned_data["admin_areas"]

        if location == "0":
            msg = "Select which location the barrier relates to"
            self.add_error("location_select", msg)

        trading_bloc_codes = [
            trading_bloc["code"] for trading_bloc in self.trading_blocs
        ]
        if location in trading_bloc_codes:
            self.cleaned_data["country"] = None
            self.cleaned_data["trading_bloc"] = location
        else:
            self.cleaned_data["country"] = location
            self.cleaned_data["trading_bloc"] = ""

        # Set trading bloc values if it is indicated a trading bloc is the cause
        self.cleaned_data["caused_by_trading_bloc"] = False
        if (
            self.cleaned_data["trading_bloc_EU"] == "YES"
            or self.cleaned_data["trading_bloc_GCC"] == "YES"
            or self.cleaned_data["trading_bloc_Mercosur"] == "YES"
            or self.cleaned_data["trading_bloc_EAEU"] == "YES"
        ):
            self.cleaned_data["caused_by_trading_bloc"] = True

        # Trigger error if admin areas haven't been selected but user has indicated
        # barrier is not country-wide
        if (
            self.cleaned_data["affect_whole_country"] is False
            and selected_admin_areas == ""
        ):
            msg = "Select all admin areas the barrier relates to"
            self.add_error("admin_areas", msg)

        # Turn admin areas data to list & set caused by value
        self.cleaned_data["admin_areas"] = selected_admin_areas.split(",")
        if self.cleaned_data["admin_areas"] != [""]:
            self.cleaned_data["caused_by_admin_areas"] = True
        else:
            self.cleaned_data["admin_areas"] = []
            self.cleaned_data["caused_by_admin_areas"] = False

        return cleaned_data

    def get_trading_bloc_fields(self):
        for field_name in self.fields:
            if field_name.startswith("trading_bloc_"):
                yield self[field_name]


class BarrierTradeDirectionForm(APIFormMixin, forms.Form):
    trade_direction = forms.ChoiceField(
        label="Which trade direction does this barrier affect?",
        choices=(
            ("1", "Exporting from the UK or investing overseas"),
            ("2", "Importing or investing into the UK"),
        ),
        error_messages={"required": "Select the trade direction this barrier affects"},
        widget=forms.RadioSelect,
    )


class BarrierSectorsAffectedForm(APIFormMixin, forms.Form):
    main_sector = forms.CharField(
        label="Main sector affected",
        help_text=("Add the sector affected the most by the barrier"),
        error_messages={"required": "Select the sector affected the most"},
    )
    sectors = forms.CharField(
        label="Other sectors (optional)",
        help_text=("Add all the other sectors affected by the barrier"),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        cleaned_sectors = []
        if cleaned_data["sectors"]:
            cleaned_sectors = json.loads(cleaned_data["sectors"])
        cleaned_data["sectors"] = cleaned_sectors
        cleaned_data["sectors_affected"] = True


class BarrierCompaniesAffectedForm(APIFormMixin, forms.Form):
    companies_affected = forms.CharField(
        label="Name of company affected by the barrier",
        help_text=(
            "Add at least one company. You can search by name, address or company number"
        ),
        widget=forms.HiddenInput(),
    )
    unrecognised_company = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()

        # Convert the passed companies string to list of dictionaries
        companies_list = []
        if cleaned_data["companies_affected"] != "None":
            companies_list = json.loads(cleaned_data["companies_affected"])
        added_companies_list = []
        if cleaned_data["unrecognised_company"] != "":
            added_companies_list = json.loads(cleaned_data["unrecognised_company"])

        # Need to error if none detected in lists
        if companies_list == [] and added_companies_list == []:
            msg = "Add all companies affected by the barrier."
            self.add_error("companies_affected", msg)

        # Setup list to contain the cleaned company information
        cleaned_companies_list = []
        cleaned_added_companies_list = []

        # Loop the passed companies, get their ID and name,
        # put them into a dict and append to the list
        for company in companies_list:
            cleaned_company = {
                "id": company["company_number"],
                "name": company["title"],
            }
            cleaned_companies_list.append(cleaned_company)

        # Loop through added companies and convert the string in the existing
        # data to objects
        for company in added_companies_list:
            cleaned_company = {"id": "", "name": company}
            cleaned_added_companies_list.append(cleaned_company)

        # Update cleaned_data
        cleaned_data["companies"] = cleaned_companies_list
        cleaned_data["related_organisations"] = cleaned_added_companies_list

        return cleaned_data


class BarrierExportTypeForm(APIFormMixin, forms.Form):
    export_types = forms.MultipleChoiceField(
        label="Which types of exports does the barrier affect?",
        help_text="Select all that apply",
        choices=EXPORT_TYPES,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "govuk-checkboxes__input"}),
        error_messages={
            "required": "Select the types of exports the barrier affects.",
        },
    )
    export_description = forms.CharField(
        label="Which goods, services or investments does the barrier affect?",
        help_text=(
            """
            Enter all goods, services or investments affected.
            Be as specific as you can. Put each item on a new line.
            """
        ),
        error_messages={
            "required": "Enter all goods, services or investments the barrier affects.",
        },
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": 5,
            },
        ),
    )
    code = forms.CharField(
        label="Enter an HS commodity code (optional)",
        help_text=(
            "Enter your HS commodity code below ignoring any spaces or full stops. "
            "You can also copy and paste multiple codes separated by commas "
            "into the first box (there is no limit). Only numbers and commas "
            "will be recognised, all other punctuation and characters will be ignored."
        ),
        error_messages={"required": "Enter an HS commodity code"},
        widget=CommodityCodeWidget,
        required=False,
    )
    location = forms.ChoiceField(
        label="Which location are the HS commodity codes from?",
        choices=[],
        error_messages={"required": "Select a location"},
        required=False,
    )

    codes = MultipleValueField(required=False)
    countries = MultipleValueField(required=False)
    trading_blocs = MultipleValueField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        codes = cleaned_data.get("codes", [])
        countries = cleaned_data["countries"]
        trading_blocs = cleaned_data["trading_blocs"]
        # Mixed lists length will not match could have some countries and some trading blocs
        # In that case take first country code
        matched_lists = True
        default_country = ""
        default_trading = ""
        if len(codes) != len(countries) or len(codes) != len(trading_blocs):
            # lists don't match use first country in list
            matched_lists = False
            if len(countries):
                default_country = countries[0]
            else:
                # No country available we should have a trading bloc
                default_trading = trading_blocs[0]

        self.commodities = []
        for index, code in enumerate(codes):
            try:
                if matched_lists:
                    self.commodities.append(
                        {
                            "code": code,
                            "country": countries[index] or None,
                            "trading_bloc": trading_blocs[index] or "",
                        }
                    )
                elif default_country:
                    self.commodities.append(
                        {
                            "code": code,
                            "country": default_country,
                            "trading_bloc": "",
                        }
                    )
                else:
                    self.commodities.append(
                        {
                            "code": code,
                            "country": None,
                            "trading_bloc": default_trading,
                        }
                    )

            except IndexError:
                raise forms.ValidationError("Code/country mismatch")
        cleaned_data["commodities"] = self.commodities
        return cleaned_data


class BarrierDetailsSummaryForm(forms.Form):
    details_confirmation = forms.CharField(
        widget=forms.HiddenInput(),
    )
