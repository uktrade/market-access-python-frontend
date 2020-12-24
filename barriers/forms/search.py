import copy
from operator import itemgetter
from urllib.parse import urlencode

from django import forms
from django.http import QueryDict


class BarrierSearchForm(forms.Form):
    search_id = forms.UUIDField(required=False, widget=forms.HiddenInput())
    search = forms.CharField(label="Search barrier title, summary, code or PID", max_length=255, required=False)
    country = forms.MultipleChoiceField(label="Barrier location", required=False,)
    country_trading_bloc = forms.MultipleChoiceField(label="Country trading blocs", required=False,)
    extra_location = forms.MultipleChoiceField(label="Barrier location", required=False,)
    trade_direction = forms.MultipleChoiceField(label="Trade direction", required=False,)
    sector = forms.MultipleChoiceField(label="Sector", required=False,)
    organisation = forms.MultipleChoiceField(label="Government organisations", required=False,)
    category = forms.MultipleChoiceField(label="Category", required=False,)
    region = forms.MultipleChoiceField(label="Overseas region", required=False,)
    priority = forms.MultipleChoiceField(label="Barrier priority", required=False,)
    status = forms.MultipleChoiceField(label="Barrier status", required=False,)
    tags = forms.MultipleChoiceField(label="Tags", required=False,)
    user = forms.BooleanField(label="My barriers", required=False,)
    team = forms.BooleanField(label="My team barriers", required=False,)
    member = forms.IntegerField(label="People", required=False)
    only_archived = forms.BooleanField(label="Only archived barriers", required=False,)
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
        ),
        required=False,
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
            ("with", "With an economic impact assessment"),
            ("without", "Without an economic impact assessment"),
        ),
        required=False,
    )
    commodity_code = forms.MultipleChoiceField(
        label="HS commodity code",
        choices=(
            ("with", "With an hs commodity code"),
            ("without", "Without an hs commodity code"),
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

    filter_groups = {
        "show": {"label": "Show", "fields": ("user", "team", "only_archived")},
        "country": {"label": "Barrier location", "fields": ("extra_location", "country_trading_bloc")},
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
        self.set_priority_choices()
        self.set_status_choices()
        self.set_tags_choices()
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
            "extra_location": data.getlist("extra_location"),
            "trade_direction": data.getlist("trade_direction"),
            "sector": data.getlist("sector"),
            "organisation": data.getlist("organisation"),
            "category": data.getlist("category"),
            "region": data.getlist("region"),
            "priority": data.getlist("priority"),
            "status": data.getlist("status"),
            "tags": data.getlist("tags"),
            "user": data.get("user"),
            "team": data.get("team"),
            "member": data.get("member"),
            "only_archived": data.get("only_archived"),
            "wto": data.getlist("wto"),
            "public_view": data.getlist("public_view"),
            "economic_assessment": data.getlist("economic_assessment"),
            "economic_impact_assessment": data.getlist("economic_impact_assessment"),
            "commodity_code": data.getlist("commodity_code"),
            "commercial_value_estimate": data.getlist("commercial_value_estimate"),
        }
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
        }
        self.fields["extra_location"].choices = [
            (
                trading_bloc["code"],
                trading_bloc_labels.get(trading_bloc["code"], trading_bloc["name"])
            ) for trading_bloc in self.metadata.get_trading_bloc_list()
        ]

    def set_country_trading_bloc_choices(self):
        trading_bloc_labels = {
            "TB00016": "Include country specific implementations of EU regulations"
        }
        self.fields["country_trading_bloc"].choices = [
            (
                trading_bloc["code"],
                trading_bloc_labels.get(trading_bloc["code"], trading_bloc["name"])
            ) for trading_bloc in self.metadata.get_trading_bloc_list()
        ]

    def set_trade_direction_choices(self):
        self.fields["trade_direction"].choices = self.metadata.get_trade_direction_choices()

    def set_sector_choices(self):
        self.fields["sector"].choices = [
            (sector["id"], sector["name"])
            for sector in self.metadata.get_sector_list(level=0)
        ]

    def set_organisation_choices(self):
        self.fields["organisation"].choices = self.metadata.get_gov_organisation_choices()

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

    def set_priority_choices(self):
        priorities = self.metadata.data["barrier_priorities"]
        priorities.sort(key=itemgetter("order"))
        choices = [
            (
                priority["code"],
                (
                    f"<span class='priority-marker "
                    f"priority-marker--{ priority['code'].lower() }'>"
                    f"</span>{priority['name']}"
                ),
            )
            for priority in priorities
        ]
        self.fields["priority"].choices = choices

    def set_status_choices(self):
        status_ids = ("1", "2", "3", "4", "5", "7")
        choices = [
            (id, value)
            for id, value in self.metadata.data["barrier_status"].items()
            if id in status_ids
        ]
        choices.sort(key=itemgetter(0))
        self.fields["status"].choices = choices

    def set_tags_choices(self):
        choices = [
            (str(tag['id']), tag['title'])
            for tag in self.metadata.get_barrier_tags()
        ]
        choices.sort(key=itemgetter(0))
        self.fields["tags"].choices = choices

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
        return urlencode(params, doseq=True)

    def get_api_search_parameters(self):
        params = {}
        params["search_id"] = self.cleaned_data.get("search_id")
        params["search"] = self.cleaned_data.get("search")
        params["location"] = ",".join(
            self.cleaned_data.get("country", []) + self.cleaned_data.get("region", [])
            + self.cleaned_data.get("extra_location", [])
        )
        params["trade_direction"] = ",".join(self.cleaned_data.get("trade_direction", []))
        params["sector"] = ",".join(self.cleaned_data.get("sector", []))
        params["organisation"] = ",".join(self.cleaned_data.get("organisation", []))
        params["category"] = ",".join(self.cleaned_data.get("category", []))
        params["priority"] = ",".join(self.cleaned_data.get("priority", []))
        params["status"] = ",".join(self.cleaned_data.get("status", []))
        params["tags"] = ",".join(self.cleaned_data.get("tags", []))
        params["team"] = self.cleaned_data.get("team")
        params["user"] = self.cleaned_data.get("user")
        params["member"] = self.cleaned_data.get("member")
        params["wto"] = ",".join(self.cleaned_data.get("wto", []))
        params["archived"] = self.cleaned_data.get("only_archived") or "0"
        params["public_view"] = ",".join(self.cleaned_data.get("public_view", []))
        params["country_trading_bloc"] = ",".join(self.cleaned_data.get("country_trading_bloc", []))
        params["economic_assessment"] = ",".join(self.cleaned_data.get("economic_assessment", []))
        params["economic_impact_assessment"] = ",".join(self.cleaned_data.get("economic_impact_assessment", []))
        params["commodity_code"] = ",".join(self.cleaned_data.get("commodity_code", []))
        params["commercial_value_estimate"] = ",".join(self.cleaned_data.get("commercial_value_estimate", []))

        return {k: v for k, v in params.items() if v}

    def get_raw_filters(self):
        """
        Get the currently applied filters in the same format as cleaned_data.
        """
        return {
            key: value
            for key, value in self.cleaned_data.items()
            if value and not self.fields[key].widget.is_hidden
        }

    def get_raw_filters_querystring(self):
        return urlencode(self.get_raw_filters(), doseq=True)

    def get_filter_readable_value(self, field_name, value):
        field = self.fields[field_name]
        if hasattr(field, "choices"):
            field_lookup = dict(field.choices)
            return ", ".join([field_lookup.get(x) for x in value])
        elif isinstance(field, forms.BooleanField):
            return field.label
        return value

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
                filters[key] = {
                    "label": self.get_filter_label(name),
                    "value": self.get_filter_value(name, value),
                    "readable_value": self.get_filter_readable_value(name, value),
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
