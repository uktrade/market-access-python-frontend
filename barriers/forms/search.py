import copy
import logging
from operator import itemgetter
from urllib.parse import urlencode

from django import forms
from django.conf import settings
from django.http import QueryDict

from barriers.constants import DEPRECATED_TAGS, EXPORT_TYPES, STATUS_WITH_DATE_FILTER
from utils.forms.fields import MonthDateRangeField
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
    only_main_sector = forms.BooleanField(label="Only main sector", required=False)
    organisation = forms.MultipleChoiceField(
        label="Government organisations",
        required=False,
    )
    category = forms.MultipleChoiceField(
        label="Category",
        required=False,
    )
    policy_team = forms.MultipleChoiceField(
        label="Policy team",
        required=False,
    )
    region = forms.MultipleChoiceField(
        label="Overseas region",
        required=False,
    )
    # Combined priority field combining Top 100 and Priority level
    combined_priority = forms.MultipleChoiceField(
        label="Barrier priority",
        choices=(
            ("APPROVED", "Top 100 priority"),
            ("APPROVAL_PENDING", "Top 100 approval pending"),
            ("REMOVAL_PENDING", "Top 100 removal pending"),
            ("RESOLVED", "Top 100 priority resolved"),
            ("OVERSEAS", "Overseas Delivery"),
            ("WATCHLIST", "Watch list"),
            ("NONE", "No priority assigned"),
        ),
        # Provide tuple and match to choices to display help text relevant to choice
        help_text=(("APPROVED", "Includes removal pending"),),
        required=False,
    )

    status = forms.MultipleChoiceField(
        label="Barrier status",
        required=False,
    )

    status_date_resolved_in_full = MonthDateRangeField(
        label="Resolved date", required=False
    )
    status_date_resolved_in_part = MonthDateRangeField(
        label="Resolved in part date",
        required=False,
    )
    status_date_open_in_progress = MonthDateRangeField(
        label="Estimated resolution date", required=False
    )
    start_date = MonthDateRangeField(
        label="Barrier start date",
        required=False,
    )

    tags = forms.MultipleChoiceField(
        label="Tags",
        required=False,
    )
    delivery_confidence = forms.MultipleChoiceField(
        label="Delivery confidence",
        choices=(
            ("ON_TRACK", "On Track"),
            ("RISK_OF_DELAY", "Risk of delay"),
            ("DELAYED", "Delayed"),
        ),
        required=False,
    )
    export_types = forms.MultipleChoiceField(
        label="Export type",
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
        label="Barrier publication",
        choices=(
            ("unknown", "To be decided"),
            ("allowed", "Allowed to be published"),
            ("not_allowed", "Not allowed to be published"),
            ("awaiting_approval", "Awaiting Approval"),
            ("ready_for_publishing", "Awaiting Publishing"),
            ("published", "Published"),
            ("unpublished", "Unpublished"),
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
        label="Economic impact assessment",
        choices=(
            ("with", "With an Economic impact assessment"),
            ("without", "Without an Economic impact assessment"),
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
    valuation_assessment = forms.MultipleChoiceField(
        label="Valuation assessment",
        choices=(
            ("with", "With a valuation assessment"),
            ("without", "Without a valuation assessment"),
        ),
        required=False,
    )

    filter_groups = {
        "show": {"label": "Show", "fields": ("user", "team", "only_archived")},
        "country": {
            "label": "Barrier location",
            "fields": ("extra_location", "country_trading_bloc"),
        },
        "action_plans": {"label": "Action plans", "fields": ("has_action_plan",)},
        "status": {
            "label": "Barrier status",
            "fields": (
                "status_date_resolved_in_full",
                "status_date_resolved_in_part",
                "status_date_open_in_progress",
            ),
        },
    }

    def __init__(self, metadata, *args, **kwargs):
        self.metadata = metadata

        # we need to use some trickery here as we're initialising the form with a QueryDict from GET data, so we need to
        # check if the field requires multiple values, or if it only needs one. That decides how we retrieve it from the
        # QueryDict object
        if isinstance(kwargs["data"], QueryDict):
            new_data = {}
            for key, value in kwargs["data"].items():
                mapped_field = self.declared_fields.get(key, None)
                if isinstance(mapped_field, forms.Field):
                    # the data in the QueryDict matches a field on the form, let's check if it's a multiple choice field
                    # or a single-value field
                    if isinstance(mapped_field, forms.MultipleChoiceField):
                        # it's multiple, use getlist to get the list of values
                        new_data[key] = kwargs["data"].getlist(key)
                    else:
                        # it's single, use get to get the value
                        new_data[key] = kwargs["data"].get(key)
                else:
                    new_data[key] = value
            kwargs["data"] = new_data

        super().__init__(*args, **kwargs)

        self.set_country_choices()
        self.set_country_trading_bloc_choices()
        self.set_extra_location_choices()
        self.set_trade_direction_choices()
        self.set_sector_choices()
        self.set_organisation_choices()
        self.set_category_choices()
        self.set_policy_team_choices()
        self.set_region_choices()
        self.set_status_choices()
        self.set_tags_choices()
        self.set_ordering_choices()
        self.index_filter_groups()

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
            "TB00003": "Include ASEAN-wide barriers",
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
            "TB00003": "Include country specific implementations of ASEAN regulations",
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
        self.fields["trade_direction"].choices = (
            self.metadata.get_trade_direction_choices()
        )

    def set_sector_choices(self):
        self.fields["sector"].choices = [
            (sector["id"], sector["name"])
            for sector in self.metadata.get_sector_list(level=0)
        ]

    def set_organisation_choices(self):
        self.fields["organisation"].choices = (
            self.metadata.get_gov_organisation_choices()
        )

    def set_category_choices(self):
        choices = [
            (str(category["id"]), category["title"])
            for category in self.metadata.data["categories"]
        ]
        choices = list(set(choices))
        choices.sort(key=itemgetter(1))
        self.fields["category"].choices = choices

    def set_policy_team_choices(self):
        choices = [
            (str(policy_team["id"]), policy_team["title"])
            for policy_team in self.metadata.data["policy_teams"]
        ]
        self.fields["policy_team"].choices = choices

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
        self.fields["tags"].choices = choices

    def set_ordering_choices(self):
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
            del params[field_name]

        if field_name == "status":
            for status_value in STATUS_WITH_DATE_FILTER:
                if f"status_date_{status_value}" in params:
                    del params[f"status_date_{status_value}"]

        # tss-1069 - we need to encode the admin_areas as string JSON in the URL
        if "admin_areas" in params:
            params = format_dict_for_url_querystring(params, ["admin_areas"])

        return urlencode(params, doseq=True)

    def get_api_search_parameters(self):
        params = {}
        params["search_id"] = self.cleaned_data.get("search_id")
        params["search"] = self.cleaned_data.get("search")
        # params["location"] = ",".join(
        #     self.cleaned_data.get("country", [])
        #     + self.cleaned_data.get("region", [])
        #     + self.cleaned_data.get("extra_location", [])
        # )
        params["region"] = self.cleaned_data.get("region", [])
        params["country"] = self.cleaned_data.get("country", [])

        params["admin_areas"] = ",".join(self.format_admin_areas())
        params["trade_direction"] = ",".join(
            self.cleaned_data.get("trade_direction", [])
        )
        # params["sector"] = ",".join(self.cleaned_data.get("sector", []))
        params["sector"] = self.cleaned_data.get("sector", [])
        params["ignore_all_sectors"] = self.cleaned_data.get("ignore_all_sectors")
        params["organisation"] = ",".join(self.cleaned_data.get("organisation", []))
        params["category"] = ",".join(self.cleaned_data.get("category", []))
        params["policy_team"] = ",".join(self.cleaned_data.get("policy_team", []))
        params["status"] = ",".join(self.cleaned_data.get("status", []))
        params["tags"] = ",".join(self.cleaned_data.get("tags", []))
        for status_value in STATUS_WITH_DATE_FILTER:
            params[f"status_date_{status_value}"] = self.cleaned_data.get(
                f"status_date_{status_value}"
            )

        params["delivery_confidence"] = ",".join(
            self.cleaned_data.get("delivery_confidence", [])
        )
        params["top_priority_status"] = ",".join(
            self.cleaned_data.get("top_priority_status", [])
        )
        params["priority_level"] = ",".join(self.cleaned_data.get("priority_level", []))
        params["combined_priority"] = ",".join(
            self.cleaned_data.get("combined_priority", [])
        )
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
        params["start_date"] = self.cleaned_data.get("start_date")
        params["only_main_sector"] = self.cleaned_data.get("only_main_sector")
        params["valuation_assessment"] = ",".join(
            self.cleaned_data.get("valuation_assessment", [])
        )

        return {k: v for k, v in params.items() if v}

    def format_admin_areas(self):
        admin_areas = []
        if self.cleaned_data.get("admin_areas"):
            for key, value in self.cleaned_data.get("admin_areas").items():
                for admin_area_id in value:
                    admin_areas.append(admin_area_id)
        return admin_areas

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
            admin_areas_selected = []
            for country in value:
                for admin_area_id in value[country]:
                    admin_area_detail = self.metadata.get_admin_area(admin_area_id)
                    admin_areas_selected.append(admin_area_detail["name"])
            return ", ".join(admin_areas_selected)
        elif isinstance(field, MonthDateRangeField):
            # it's a string of two dates, so let's just use the decompress() method of the
            # widget to get the readable value. It will return [[from_month, from_year], [to_month, to_year]
            date_range = field.widget.decompress(value)
            return f"{date_range[0][0]}/{date_range[0][1]} to {date_range[1][0]}/{date_range[1][1]}"

        return value

    def get_readable_filters(self, with_remove_urls=True):
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

                if with_remove_urls:
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
