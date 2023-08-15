import calendar
import copy
import logging
from operator import itemgetter
from urllib.parse import urlencode

from django import forms
from django.conf import settings
from django.http import QueryDict

from barriers.constants import DEPRECATED_TAGS, EXPORT_TYPES, STATUS_WITH_DATE_FILTER
from utils.forms import DateRangeField
from utils.helpers import format_dict_for_url_querystring

logger = logging.getLogger(__name__)


class BarrierSearchForm(forms.Form):
    search_id = forms.UUIDField(required=False, widget=forms.HiddenInput())
    search = forms.CharField(
        label="Search barrier title, summary, company, export description, code or PID",
        max_length=255,
        required=False,
    )
    country = forms.MultipleChoiceField(
        label="Barrier location",
        required=False,
    )
    country_trading_bloc = forms.MultipleChoiceField(
        label="Country trading blocs",
        required=False,
    )
    admin_areas = forms.JSONField(
        label="Barrier region/state",
        required=False,
    )
    extra_location = forms.MultipleChoiceField(
        label="Barrier location",
        required=False,
    )
    trade_direction = forms.MultipleChoiceField(
        label="Trade direction",
        required=False,
    )
    ignore_all_sectors = forms.BooleanField(label="Ignore all sectors", required=False)
    sector = forms.MultipleChoiceField(
        label="Sector",
        required=False,
    )
    organisation = forms.MultipleChoiceField(
        label="Government organisations",
        required=False,
    )
    category = forms.MultipleChoiceField(
        label="Category",
        required=False,
    )
    region = forms.MultipleChoiceField(
        label="Overseas region",
        required=False,
    )
    top_priority_status = forms.MultipleChoiceField(
        label="Top 100 priority barrier",
        choices=(
            ("APPROVED", "Top 100 priority"),
            ("APPROVAL_PENDING", "Approval pending"),
            ("REMOVAL_PENDING", "Removal pending"),
            ("RESOLVED", "Resolved top 100 priority"),
        ),
        # Provide tuple and match to choices to display help text relevent to choice
        help_text=(("APPROVED", "Includes removal pending"),),
        required=False,
    )
    priority_level = forms.MultipleChoiceField(
        label="Barrier priority",
        choices=(
            ("REGIONAL", "Regional priority"),
            ("COUNTRY", "Country priority"),
            ("WATCHLIST", "Watch list"),
            ("NONE", "No priority assigned"),
        ),
    )
    status = forms.MultipleChoiceField(
        label="Barrier status",
        required=False,
    )

    # Resolved date filter inputs for status: 'Resolved: In full' - status_id is 4
    resolved_date_from_month_resolved_in_full = forms.CharField(
        label="Resolved date from", help_text="Example, 01 2021", required=False
    )
    resolved_date_from_year_resolved_in_full = forms.CharField(required=False)
    resolved_date_to_month_resolved_in_full = forms.CharField(
        label="Resolved date to", help_text="Example, 01 2022", required=False
    )
    resolved_date_to_year_resolved_in_full = forms.CharField(required=False)

    # Resolved date filter inputs for status: 'Resolved: In part' - status_id is 3
    resolved_date_from_month_resolved_in_part = forms.CharField(
        label="Resolved date from", help_text="Example, 01 2021", required=False
    )
    resolved_date_from_year_resolved_in_part = forms.CharField(required=False)
    resolved_date_to_month_resolved_in_part = forms.CharField(
        label="Resolved date to", help_text="Example, 01 2022", required=False
    )
    resolved_date_to_year_resolved_in_part = forms.CharField(required=False)

    # Estimated resolution date filter inputs for status: 'Open: In progress' - status_id is 2
    resolved_date_from_month_open_in_progress = forms.CharField(
        label="Estimated resolution date from",
        help_text="Example, 01 2021",
        required=False,
    )
    resolved_date_from_year_open_in_progress = forms.CharField(required=False)
    resolved_date_to_month_open_in_progress = forms.CharField(
        label="Estimated resolution date to",
        help_text="Example, 01 2022",
        required=False,
    )
    resolved_date_to_year_open_in_progress = forms.CharField(required=False)

    tags = forms.MultipleChoiceField(
        label="Tags",
        required=False,
    )
    delivery_confidence = forms.MultipleChoiceField(
        label="Delivery Confidence",
        choices=(
            ("ON_TRACK", "On Track"),
            ("RISK_OF_DELAY", "Risk of delay"),
            ("DELAYED", "Delayed"),
        ),
        required=False,
    )
    export_types = forms.MultipleChoiceField(
        label="Export types",
        choices=EXPORT_TYPES,
        required=False,
    )
    has_action_plan = forms.BooleanField(label="Has action plan", required=False)
    user = forms.BooleanField(
        label="Barriers I have created",
        required=False,
    )
    team = forms.BooleanField(
        label="Barriers I own or am working on",
        required=False,
    )
    member = forms.IntegerField(label="People", required=False)
    only_archived = forms.BooleanField(
        label="Only archived barriers",
        required=False,
    )
    wto = forms.MultipleChoiceField(
        label="WTO",
        choices=(
            ("wto_has_been_notified", "Notified"),
            ("wto_should_be_notified", "Not notified but should be"),
            ("has_committee_raised_in", "Raised"),
            ("has_raised_date", "Discussed bilaterally"),
            ("has_case_number", "Subject to a dispute settlement"),
            ("has_no_information", "No WTO information provided"),
        ),
        required=False,
    )
    public_view = forms.MultipleChoiceField(
        label="Public view",
        choices=(
            ("not_yet_sifted", "Not yet sifted"),
            ("eligible", "Allowed to be published"),
            ("ineligible", "Not allowed to be published"),
            ("ready", "Ready to publish"),
            ("published", "Published"),
            ("changed", "Barriers changed internally since being made public"),
            ("unpublished", "Unpublished"),
            ("review_later", "Barriers marked as 'review later'"),
        ),
        required=False,
    )
    economic_assessment_eligibility = forms.MultipleChoiceField(
        label="Economic assessment eligibility",
        choices=(
            ("eligible", "Eligible"),
            ("ineligible", "Ineligible"),
            ("not_yet_marked", "Not yet marked"),
        ),
    )
    economic_assessment = forms.MultipleChoiceField(
        label="Economic assessment",
        choices=(
            ("with", "With an economic assessment"),
            ("without", "Without an economic assessment"),
            ("ready_for_approval", "With an economic assessment ready for approval"),
        ),
        required=False,
    )
    economic_impact_assessment = forms.MultipleChoiceField(
        label="Valuation assessment",
        choices=(
            ("with", "With a valuation assessment"),
            ("without", "Without a valuation assessment"),
        ),
        required=False,
    )
    commodity_code = forms.MultipleChoiceField(
        label="HS commodity code",
        choices=(
            ("with", "With an HS commodity code"),
            ("without", "Without an HS commodity code"),
        ),
        required=False,
    )
    commercial_value_estimate = forms.MultipleChoiceField(
        label="Commercial value estimate",
        choices=(
            ("with", "With a commercial value estimate"),
            ("without", "Without a commercial value estimate"),
        ),
        required=False,
    )
    ordering = forms.ChoiceField(
        label="Sort by",
        choices=(),
        required=False,
        widget=forms.Select(
            attrs={"class": "govuk-select dmas-search-ordering-select"}
        ),
    )

    start_date = DateRangeField(label="Barrier Start date", required=False)
    start_date_from_month = forms.CharField(
        label="Barrier Start date from month",
        help_text="Example, 01 2021",
        required=False,
    )
    start_date_from_year = forms.CharField(
        label="Barrier Start date from year", required=False
    )
    start_date_to_month = forms.CharField(
        label="Barrier Start date to month",
        help_text="Example, 01 2022",
        required=False,
    )
    start_date_to_year = forms.CharField(
        label="Barrier Start date to year", required=False
    )

    filter_groups = {
        "show": {"label": "Show", "fields": ("user", "team", "only_archived")},
        "country": {
            "label": "Barrier location",
            "fields": ("extra_location", "country_trading_bloc"),
        },
        "action_plans": {"label": "Action plans", "fields": ("has_action_plan",)},
    }

    def __init__(self, metadata, *args, **kwargs):
        self.metadata = metadata

        if isinstance(kwargs["data"], QueryDict):
            kwargs["data"] = self.get_data_from_querydict(kwargs["data"])

        super().__init__(*args, **kwargs)
        self.set_country_choices()
        self.set_country_trading_bloc_choices()
        self.set_extra_location_choices()
        self.set_trade_direction_choices()
        self.set_sector_choices()
        self.set_organisation_choices()
        self.set_category_choices()
        self.set_region_choices()
        self.set_status_choices()
        self.set_tags_choices()
        self.set_ordering_choices()
        self.index_filter_groups()

    def get_data_from_querydict(self, data):
        """
        Get form data from the GET parameters.
        """
        cleaned_data = {
            "search_id": data.get("search_id"),
            "search": data.get("search"),
            "country": data.getlist("country"),
            "country_trading_bloc": data.getlist("country_trading_bloc"),
            "admin_areas": data.get("admin_areas"),
            "extra_location": data.getlist("extra_location"),
            "trade_direction": data.getlist("trade_direction"),
            "sector": data.getlist("sector"),
            "ignore_all_sectors": data.get("ignore_all_sectors"),
            "organisation": data.getlist("organisation"),
            "category": data.getlist("category"),
            "region": data.getlist("region"),
            "top_priority_status": data.getlist("top_priority_status"),
            "priority_level": data.getlist("priority_level"),
            "status": data.getlist("status"),
            "tags": data.getlist("tags"),
            "delivery_confidence": data.getlist("delivery_confidence"),
            "has_action_plan": data.get("has_action_plan"),
            "user": data.get("user"),
            "team": data.get("team"),
            "member": data.get("member"),
            "only_archived": data.get("only_archived"),
            "wto": data.getlist("wto"),
            "public_view": data.getlist("public_view"),
            "economic_assessment_eligibility": data.getlist(
                "economic_assessment_eligibility"
            ),
            "economic_assessment": data.getlist("economic_assessment"),
            "economic_impact_assessment": data.getlist("economic_impact_assessment"),
            "commodity_code": data.getlist("commodity_code"),
            "commercial_value_estimate": data.getlist("commercial_value_estimate"),
            "ordering": data.get("ordering"),
            "start_date_from_month": data.get("start_date_from_month"),
            "start_date_from_year": data.get("start_date_from_year"),
            "start_date_to_month": data.get("start_date_to_month"),
            "start_date_to_year": data.get("start_date_to_year"),
            "export_types": data.getlist("export_types"),
        }

        for status_value in STATUS_WITH_DATE_FILTER:
            cleaned_data[f"resolved_date_from_month_{status_value}"] = data.get(
                f"resolved_date_from_month_{status_value}"
            )
            cleaned_data[f"resolved_date_from_year_{status_value}"] = data.get(
                f"resolved_date_from_year_{status_value}"
            )
            cleaned_data[f"resolved_date_to_month_{status_value}"] = data.get(
                f"resolved_date_to_month_{status_value}"
            )
            cleaned_data[f"resolved_date_to_year_{status_value}"] = data.get(
                f"resolved_date_to_year_{status_value}"
            )

        return {k: v for k, v in cleaned_data.items() if v}

    def set_country_choices(self):
        location_choices = [
            (trading_bloc["code"], trading_bloc["name"])
            for trading_bloc in self.metadata.get_trading_bloc_list()
        ] + [
            (country["id"], country["name"])
            for country in self.metadata.get_country_list()
        ]
        self.fields["country"].choices = location_choices

    def set_extra_location_choices(self):
        trading_bloc_labels = {
            "TB00016": "Include EU-wide barriers",
            "TB00026": "Include Mercosur-wide barriers",
            "TB00013": "Include EAEU-wide barriers",
            "TB00017": "Include GCC-wide barriers",
        }
        self.fields["extra_location"].choices = [
            (
                trading_bloc["code"],
                trading_bloc_labels.get(trading_bloc["code"], trading_bloc["name"]),
            )
            for trading_bloc in self.metadata.get_trading_bloc_list()
        ]

    def set_country_trading_bloc_choices(self):
        trading_bloc_labels = {
            "TB00016": "Include country specific implementations of EU regulations",
            "TB00026": (
                "Include country specific implementations of Mercosur regulations"
            ),
            "TB00013": "Include country specific implementations of EAEU regulations",
            "TB00017": "Include country specific implementations of GCC regulations",
        }
        self.fields["country_trading_bloc"].choices = [
            (
                trading_bloc["code"],
                trading_bloc_labels.get(trading_bloc["code"], trading_bloc["name"]),
            )
            for trading_bloc in self.metadata.get_trading_bloc_list()
        ]

    def set_trade_direction_choices(self):
        self.fields[
            "trade_direction"
        ].choices = self.metadata.get_trade_direction_choices()

    def set_sector_choices(self):
        self.fields["sector"].choices = [
            (sector["id"], sector["name"])
            for sector in self.metadata.get_sector_list(level=0)
        ]

    def set_organisation_choices(self):
        self.fields[
            "organisation"
        ].choices = self.metadata.get_gov_organisation_choices()

    def set_category_choices(self):
        choices = [
            (str(category["id"]), category["title"])
            for category in self.metadata.data["categories"]
        ]
        choices = list(set(choices))
        choices.sort(key=itemgetter(1))
        self.fields["category"].choices = choices

    def set_region_choices(self):
        choices = [
            (country["id"], country["name"])
            for country in self.metadata.get_overseas_region_list()
        ]
        self.fields["region"].choices = choices

    def set_status_choices(self):
        status_ids = ("2", "3", "4", "5")
        choices = [
            (id, value)
            for id, value in self.metadata.data["barrier_status"].items()
            if id in status_ids
        ]
        choices.sort(key=itemgetter(0))
        self.fields["status"].choices = choices

    def set_tags_choices(self):
        choices = [
            (str(tag["id"]), tag["title"])
            for tag in self.metadata.get_barrier_tag_choices("search")
            if tag["title"] not in DEPRECATED_TAGS
        ]
        choices.sort(key=itemgetter(0))
        self.fields["tags"].choices = choices

    def set_ordering_choices(self):
        choices = self.metadata.get_search_ordering_choices()
        self.fields["ordering"].choices = self.metadata.get_search_ordering_choices()

    def clean_country(self):
        data = self.cleaned_data["country"]
        if "" in data:
            data.remove("")
        return data

    def clean_region(self):
        data = self.cleaned_data["region"]
        if "" in data:
            data.remove("")
        return data

    def clean_has_action_plan(self):
        if self.cleaned_data["has_action_plan"] is True:
            return "1"

    def clean_user(self):
        if self.cleaned_data["user"] is True:
            return "1"

    def clean_team(self):
        if self.cleaned_data["team"] is True:
            return "1"

    def clean_only_archived(self):
        if self.cleaned_data["only_archived"] is True:
            return "1"

    def index_filter_groups(self):
        self.filter_group_lookup = {}
        for key, info in self.filter_groups.items():
            for field in info["fields"]:
                self.filter_group_lookup[field] = {
                    "key": key,
                    "label": info["label"],
                    "fields": info["fields"],
                }

    def get_filter_key(self, field_name):
        if field_name in self.filter_group_lookup:
            return self.filter_group_lookup[field_name]["key"]
        return field_name

    def get_filter_label(self, field_name):
        if field_name in self.filter_group_lookup:
            return self.filter_group_lookup[field_name]["label"]
        return self.fields[field_name].label

    def get_filter_value(self, field_name, value):
        if field_name in self.filter_group_lookup:
            return [value]
        return value

    def get_remove_url(self, field_name):
        params = {k: v for k, v in self.cleaned_data.items() if v}

        if field_name in self.filter_group_lookup:
            for field in self.filter_group_lookup[field_name]["fields"]:
                if field in params:
                    del params[field]
        else:
            # Clear resolved date filters if requesting a resolved status filter removal
            if field_name == "status":
                for status in STATUS_WITH_DATE_FILTER:
                    params.pop(f"resolved_date_from_month_{status}", None)
                    params.pop(f"resolved_date_from_year_{status}", None)
                    params.pop(f"resolved_date_to_month_{status}", None)
                    params.pop(f"resolved_date_to_year_{status}", None)
            elif field_name == "start_date":
                params.pop("start_date_from_month", None)
                params.pop("start_date_from_year", None)
                params.pop("start_date_to_month", None)
                params.pop("start_date_to_year", None)

            del params[field_name]

        return urlencode(params, doseq=True)

    def get_api_search_parameters(self):
        params = {}
        params["search_id"] = self.cleaned_data.get("search_id")
        params["search"] = self.cleaned_data.get("search")
        params["location"] = ",".join(
            self.cleaned_data.get("country", [])
            + self.cleaned_data.get("region", [])
            + self.cleaned_data.get("extra_location", [])
        )
        params["admin_areas"] = ",".join(self.format_admin_areas())
        params["trade_direction"] = ",".join(
            self.cleaned_data.get("trade_direction", [])
        )
        params["sector"] = ",".join(self.cleaned_data.get("sector", []))
        params["ignore_all_sectors"] = self.cleaned_data.get("ignore_all_sectors")
        params["organisation"] = ",".join(self.cleaned_data.get("organisation", []))
        params["category"] = ",".join(self.cleaned_data.get("category", []))
        params["status"] = ",".join(self.cleaned_data.get("status", []))
        params["tags"] = ",".join(self.cleaned_data.get("tags", []))
        for status_value in STATUS_WITH_DATE_FILTER:
            params[f"status_date_{status_value}"] = self.format_resolved_date(
                status_value
            )
        params["delivery_confidence"] = ",".join(
            self.cleaned_data.get("delivery_confidence", [])
        )
        params["top_priority_status"] = ",".join(
            self.cleaned_data.get("top_priority_status", [])
        )
        params["priority_level"] = ",".join(self.cleaned_data.get("priority_level", []))
        params["has_action_plan"] = self.cleaned_data.get("has_action_plan")
        params["team"] = self.cleaned_data.get("team")
        params["user"] = self.cleaned_data.get("user")
        params["member"] = self.cleaned_data.get("member")
        params["wto"] = ",".join(self.cleaned_data.get("wto", []))
        params["archived"] = self.cleaned_data.get("only_archived") or "0"
        params["public_view"] = ",".join(self.cleaned_data.get("public_view", []))
        params["country_trading_bloc"] = ",".join(
            self.cleaned_data.get("country_trading_bloc", [])
        )
        params["economic_assessment_eligibility"] = ",".join(
            self.cleaned_data.get("economic_assessment_eligibility", [])
        )
        params["economic_assessment"] = ",".join(
            self.cleaned_data.get("economic_assessment", [])
        )
        params["economic_impact_assessment"] = ",".join(
            self.cleaned_data.get("economic_impact_assessment", [])
        )
        params["commodity_code"] = ",".join(self.cleaned_data.get("commodity_code", []))
        params["commercial_value_estimate"] = ",".join(
            self.cleaned_data.get("commercial_value_estimate", [])
        )
        params["ordering"] = self.cleaned_data.get(
            "ordering", settings.API_BARRIER_LIST_DEFAULT_SORT
        )
        params["export_types"] = ",".join(self.cleaned_data.get("export_types", []))
        params["start_date"] = self.format_start_date()

        return {k: v for k, v in params.items() if v}

    def format_admin_areas(self):
        admin_areas = []
        if self.cleaned_data.get("admin_areas"):
            for key, value in self.cleaned_data.get("admin_areas").items():
                for admin_area_id in value:
                    admin_areas.append(admin_area_id)
        return admin_areas

    def format_resolved_date(self, status):
        """
        Format the resolved date input to be compatible with the API's queryset filter
        Needs to be in this format YYYY-MM-DD,YYYY-MM-DD for "from"-"to" dates
        Users only input the month and year, so we need to generate a day value.
        """

        from_year = self.cleaned_data.get(f"resolved_date_from_year_{status}")
        from_month = self.cleaned_data.get(f"resolved_date_from_month_{status}")
        to_year = self.cleaned_data.get(f"resolved_date_to_year_{status}")
        to_month = self.cleaned_data.get(f"resolved_date_to_month_{status}")

        if from_year and from_month and to_year and to_month:

            from_date = from_year + "-" + from_month + "-01"

            # calendar has function to identify last day of a given month in a year
            to_date_day = calendar.monthrange(int(to_year), int(to_month))[1]
            to_date = to_year + "-" + to_month + "-" + str(to_date_day)

            return from_date + "," + to_date

        else:
            return []

    def format_start_date(self):
        """
        Format the start date input to be compatible with the API's queryset filter
        Needs to be in this format YYYY-MM-DD,YYYY-MM-DD for "from"-"to" dates
        Users only input the month and year, so we need to generate a day value.
        """
        from_year = self.cleaned_data.get("start_date_from_year")
        from_month = self.cleaned_data.get("start_date_from_month")
        to_year = self.cleaned_data.get("start_date_to_year")
        to_month = self.cleaned_data.get("start_date_to_month")

        if from_year and from_month and to_year and to_month:

            from_date = from_year + "-" + from_month + "-01"

            # calendar has function to identify last day of a given month in a year
            to_date_day = calendar.monthrange(int(to_year), int(to_month))[1]
            to_date = to_year + "-" + to_month + "-" + str(to_date_day)

            return from_date + "," + to_date
        else:
            return []

    def get_raw_filters(self):
        """
        Get the currently applied filters in the same format as cleaned_data.
        """
        return {
            key: value
            for key, value in self.cleaned_data.items()
            if value and not self.fields[key].widget.is_hidden and not key == "ordering"
        }

    def get_raw_filters_querystring(self):

        # In some instances, filters need reformatting before being encoded
        filters_for_encode = format_dict_for_url_querystring(
            self.get_raw_filters(), ["admin_areas"]
        )

        return urlencode(filters_for_encode, doseq=True)

    def get_filter_readable_value(self, field_name, value):
        field = self.fields[field_name]

        if hasattr(field, "choices"):
            field_lookup = dict(field.choices)
            return ", ".join([field_lookup.get(x) for x in value])
        elif isinstance(field, forms.BooleanField):
            return field.label
        elif field.label == "Barrier region/state":
            return self.get_readable_admin_area_filter(value)

        return value

    def get_readable_admin_area_filter(self, admin_area_selections):
        admin_areas_selected = []
        for country in admin_area_selections:
            for admin_area_id in admin_area_selections[country]:
                admin_area_detail = self.metadata.get_admin_area(admin_area_id)
                admin_areas_selected.append(admin_area_detail["name"])
        return ", ".join(admin_areas_selected)

    def get_readable_filters(self, with_remove_links=False):
        """
        Get the currently applied filters with their readable values.

        Looks up the human-friendly value for fields with choices
        and calculates the url to remove each filter.
        """
        filters = {}

        for name, value in self.get_raw_filters().items():
            value = copy.copy(value)
            key = self.get_filter_key(name)
            if key not in filters:
                readable_value = self.get_filter_readable_value(name, value)
                if readable_value == "" or readable_value is None:
                    # Do not add filter tag if the readable value is empty, move to next filter
                    continue
                filters[key] = {
                    "label": self.get_filter_label(name),
                    "value": self.get_filter_value(name, value),
                    "readable_value": readable_value,
                }

                if with_remove_links:
                    filters[key]["remove_url"] = self.get_remove_url(name)
            else:
                existing_readable_value = filters[key]["readable_value"]
                this_readable_value = self.get_filter_readable_value(name, value)
                filters[key][
                    "readable_value"
                ] = f"{existing_readable_value}, {this_readable_value}"
                if isinstance(value, list):
                    filters[key]["value"] += value
                else:
                    filters[key]["value"].append(value)

        return filters
