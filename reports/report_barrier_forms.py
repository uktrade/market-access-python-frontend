import datetime
import json
import logging

from django import forms

from barriers.constants import REPORTABLE_STATUSES, REPORTABLE_STATUSES_HELP_TEXT, EXPORT_TYPES
from barriers.forms.mixins import APIFormMixin
from utils.forms import CommodityCodeWidget, MonthYearField, MultipleValueField, MonthYearInFutureField
from utils.metadata import MetadataMixin

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
    start_date = MonthYearInFutureField(
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

        # Setup keys for status date and summary
        cleaned_data["status_date"] = datetime.date.today()
        cleaned_data["status_summary"] = ""

        if status == "3":
            # Partially resolved date and reason requried
            if partially_resolved_date is None:
                msg = "Enter a date the barrier was partially resolved"
                self.add_error("partially_resolved_date", msg)
            if partially_resolved_description == "":
                msg = "Enter a description for partially resolved"
                self.add_error("partially_resolved_description", msg)
            cleaned_data["status_date"] = partially_resolved_date
            cleaned_data["status_summary"] = partially_resolved_description

        if status == "4":
            # Resolved date and reason requried
            if resolved_date is None:
                msg = "Enter a date the barrier was resolved"
                self.add_error("resolved_date", msg)
            if resolved_description == "":
                msg = "Enter a description for resolved"
                self.add_error("resolved_description", msg)
            cleaned_data["status_date"] = resolved_date
            cleaned_data["status_summary"] = resolved_description

        if start_date is None and start_date_known is False:
            msg = "Enter a date the barrier started to affect trade or I don't know"
            self.add_error("start_date", msg)

        if start_date_known and currently_active == "":
            msg = "Is the barrier affecting trade"
            self.add_error("currently_active", msg)

        if start_date < datetime.date.today():
            cleaned_data["currently_active"] = True
        else:
            cleaned_data["currently_active"] = False


        return cleaned_data


class BarrierLocationForm(APIFormMixin, MetadataMixin, forms.Form):
    location_select = forms.ChoiceField(
        label="Which location is affected by this issue?",
        error_messages={"required": "Select a location for this barrier"},
        help_text=(
            "A trading bloc should be selected if the barrier applies to the whole "
            "trading bloc. Select a country if the barrier is a national "
            "implementation of a trading bloc regulation (so only applies to that "
            "country)"
        ),
        required=True,
    )
    admin_areas = forms.CharField(
        label="Which admin area does the barrier apply to?",
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
                label=f"Was this barrier caused by a regulation introduced by the {short_bloc_name}",
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

        #if self.cleaned_data["location_select"] == "0":
        #    msg = "Select a country or trading bloc."
        #    self.add_error("location_select", msg)

        # Map the location selected to the correct DB field
        location = self.cleaned_data["location_select"]

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
        if (self.cleaned_data["trading_bloc_EU"] == "YES"):
            self.cleaned_data["trading_bloc"] = "TB00016"
            self.cleaned_data["caused_by_trading_bloc"] = True
        if (self.cleaned_data["trading_bloc_GCC"] == "YES"):
            self.cleaned_data["trading_bloc"] = "TB00017"
            self.cleaned_data["caused_by_trading_bloc"] = True
        if (self.cleaned_data["trading_bloc_Mercosur"] == "YES"):
            self.cleaned_data["trading_bloc"] = "TB00026"
            self.cleaned_data["caused_by_trading_bloc"] = True
        if (self.cleaned_data["trading_bloc_EAEU"] == "YES"):
            self.cleaned_data["trading_bloc"] = "TB00013"
            self.cleaned_data["caused_by_trading_bloc"] = True

        # Turn admin areas data to list & set caused by value
        self.cleaned_data["admin_areas"] = self.cleaned_data["admin_areas"].split(",")
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
        choices={
            ("1", "Exporting from the UK or investing overseas"),
            ("2", "Importing or investing into the UK"),
        },
        widget=forms.RadioSelect,
    )


class BarrierSectorsAffectedForm(APIFormMixin, forms.Form):
    # TODO get the existing sectors selectors stuff into this page
    main_sector = forms.CharField(
        label="Main sector affected",
        help_text=("Add the sector you think the barrier affects the most"),
        # choices=[],
        # widget=forms.MultipleHiddenInput(),
    )
    sectors = forms.CharField(
        label="Other sectors (optional)",
        help_text=("Add all the other sectors affected by the barrier"),
        # choices=[],
        # widget=forms.MultipleHiddenInput(),
        widget=forms.Textarea(
            attrs={
                "rows": 3,
            }
        ),
        required=False,
    )
    def clean(self):
        cleaned_data = super().clean()
        logger.critical(cleaned_data["sectors"])
        cleaned_sectors = []
        if cleaned_data["sectors"]:
            cleaned_sectors = json.loads(cleaned_data["sectors"])
        logger.critical(cleaned_sectors)
        cleaned_data["sectors"] = cleaned_sectors


class BarrierCompaniesAffectedForm(APIFormMixin, forms.Form):
    companies_affected = forms.CharField(
        label="Name of company affected by the barrier",
        help_text=("You can search by name, address or company number"),
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
            msg = "Please search for a company that has been affected by the barrier."
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
    export_type = forms.MultipleChoiceField(
        label="Which types of exports does the barrier affect?",
        help_text="Select all that apply",
        choices=EXPORT_TYPES,
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
        widget=forms.Textarea(
            attrs={
                "class": "govuk-textarea",
                "rows": 5,
            },
        ),
    )
    code = forms.CharField(
        label="Enter an HS commodity code - Optional",
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
                            "country": countries[index] or "",
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
                            "country": "",
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
