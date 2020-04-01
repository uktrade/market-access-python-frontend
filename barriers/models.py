import copy
from urllib.parse import urlencode

from .constants import ARCHIVED_REASON
from .forms.search import BarrierSearchForm

from utils.metadata import get_metadata, Statuses
from utils.models import APIModel

import dateutil.parser


class Barrier(APIModel):
    """
    Wrapper around API barrier data
    """

    _admin_areas = None
    _country = None
    _location = None
    _metadata = None
    _sectors = None
    _status = None
    _types = None

    def __init__(self, data):
        self.data = data

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = get_metadata()
        return self._metadata

    @property
    def admin_area_ids(self):
        return self.data["country_admin_areas"]

    @property
    def admin_areas(self):
        if self._admin_areas is None:
            self._admin_areas = self.metadata.get_admin_areas(self.admin_area_ids)
        return self._admin_areas

    @property
    def archived_on(self):
        return dateutil.parser.parse(self.data["archived_on"])

    @property
    def archived_reason(self):
        return ARCHIVED_REASON[self.data["archived_reason"]]

    @property
    def country(self):
        if self._country is None and self.export_country:
            self._country = self.metadata.get_country(self.export_country)
        return self._country

    @property
    def created_on(self):
        return dateutil.parser.parse(self.data["created_on"])

    @property
    def last_seen_on(self):
        return dateutil.parser.parse(self.data["last_seen_on"])

    @property
    def eu_exit_related_text(self):
        return self.metadata.get_eu_exit_related_text(self.eu_exit_related)

    @property
    def location(self):
        if self._location is None:
            self._location = self.metadata.get_location_text(
                self.data["export_country"], self.data["country_admin_areas"]
            )
        return self._location

    @property
    def modified_on(self):
        return dateutil.parser.parse(self.data["modified_on"])

    @property
    def problem_status_text(self):
        return self.metadata.get_problem_status(self.data["problem_status"])

    @property
    def reported_on(self):
        return dateutil.parser.parse(self.data["reported_on"])

    @property
    def sectors(self):
        if self._sectors is None:
            self._sectors = [
                self.metadata.get_sector(sector_id) for sector_id in self.sector_ids
            ]
        return self._sectors

    @property
    def sector_ids(self):
        return self.data["sectors"] or []

    @property
    def sector_names(self):
        if self.sectors:
            return [sector.get("name", "Unknown") for sector in self.sectors]
        return ["All sectors"]

    @property
    def source_name(self):
        return self.metadata.get_source(self.source)

    @property
    def status(self):
        if self._status is None:
            self.data["status"]["id"] = str(self.data["status"]["id"])
            self._status = self.metadata.get_status(self.data["status"]["id"])
            self._status.update(self.data["status"])
            self._status["date"] = dateutil.parser.parse(self._status["date"])
        return self._status

    @property
    def title(self):
        return self.barrier_title

    @property
    def types(self):
        if self._types is None:
            self._types = [
                self.metadata.get_barrier_type(barrier_type)
                for barrier_type in self.data["barrier_types"]
            ]
        return self._types

    @property
    def is_resolved(self):
        return self.status["id"] == "4"

    @property
    def is_partially_resolved(self):
        return self.status["id"] == "3"

    @property
    def is_open(self):
        return self.status["id"] == "2"

    @property
    def is_hibernated(self):
        return self.status["id"] == "5"


class Company(APIModel):
    """
    Wrapper around API company data
    """

    def __init__(self, data):
        self.data = data
        self.created_on = dateutil.parser.parse(data["created_on"])

    def get_address_display(self):
        address_parts = [
            self.data["address"].get("line_1"),
            self.data["address"].get("line_2"),
            self.data["address"].get("town"),
            self.data["address"].get("county"),
            self.data["address"].get("postcode"),
            self.data["address"].get("country", {}).get("name"),
        ]
        address_parts = [part for part in address_parts if part]
        return ", ".join(address_parts)


class Assessment(APIModel):
    """
    Wrapper around API assessment data
    """

    def __init__(self, data):
        self.data = data
        metadata = get_metadata()
        self.impact_text = metadata.get_impact_text(self.data.get("impact"))
        self.documents = [Document(document) for document in data["documents"]]


class Watchlist:
    """
    Wrapper around user watchlist data
    """

    _readable_filters = None

    def __init__(self, name, filters, *args, **kwargs):
        self.name = name
        self.filters = self.clean_filters(filters)

    def clean_filters(self, filters):
        """
        Node saves the watchlist search term as a list for some reason.

        We now use user=1 and team=1 instead of created_by=[1,2] (or createdBy).
        """
        if "search" in filters and isinstance(filters["search"], list):
            try:
                filters["search"] = filters["search"][0]
            except IndexError:
                filters["search"] = ""

        created_by = filters.pop("createdBy", filters.pop("created_by", []))
        if "1" in created_by:
            filters["user"] = 1
        if "2" in created_by:
            filters["team"] = 1
        return filters

    def to_dict(self):
        return {
            "name": self.name,
            "filters": self.filters,
        }

    @property
    def readable_filters(self):
        if self._readable_filters is None:
            search_form = BarrierSearchForm(metadata=get_metadata(), data=self.filters,)
            search_form.full_clean()
            self._readable_filters = search_form.get_readable_filters()
        return self._readable_filters

    @property
    def querystring(self):
        return urlencode(self.filters, doseq=True)

    def get_api_params(self):
        """
        Transform watchlist filters into api parameters
        """
        filters = copy.deepcopy(self.filters)
        region = filters.pop("region", [])
        country = filters.pop("country", [])

        if country or region:
            filters["location"] = country + region

        created_by = filters.pop("createdBy", []) + filters.pop("created_by", [])
        if "1" in created_by:
            filters["user"] = 1
        elif "2" in created_by:
            filters["team"] = 1

        filter_map = {
            "type": "barrier_type",
            "search": "text",
        }

        api_params = {}
        for name, value in filters.items():
            mapped_name = filter_map.get(name, name)
            if isinstance(value, list):
                api_params[mapped_name] = ",".join(value)
            else:
                api_params[mapped_name] = value

        return api_params


class Interaction(APIModel):
    """
    Wrapper around API interaction data
    """

    def __init__(self, data):
        self.data = data
        self.is_note = True
        self.modifier = "note"
        self.date = dateutil.parser.parse(data["created_on"])
        self.text = data["text"]
        self.user = data["created_by"]
        self.documents = [Document(document) for document in data["documents"]]

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
        }


class HistoryItem(APIModel):
    """
    Wrapper around API history item data
    """

    def __init__(self, data):
        self.data = data
        metadata = get_metadata()

        if data["field"] == "status":
            self.is_status = (True,)
            self.modifier = "status"
            self.date = dateutil.parser.parse(data["date"])
            self.event = data["field_info"]["event"]
            self.state = {
                "from": metadata.get_status_text(data["old_value"]),
                "to": metadata.get_status_text(
                    data["new_value"],
                    data["field_info"].get("sub_status"),
                    data["field_info"].get("sub_status_other"),
                ),
                "date": dateutil.parser.parse(data["field_info"]["status_date"]),
                "is_resolved": data["new_value"]
                in (Statuses.RESOLVED_IN_PART, Statuses.RESOLVED_IN_FULL,),
                "show_summary": data["new_value"]
                in (
                    Statuses.OPEN_IN_PROGRESS,
                    Statuses.UNKNOWN,
                    Statuses.OPEN_PENDING_ACTION,
                ),
            }
            self.text = data["field_info"]["status_summary"]
            self.user = data["user"]
        elif data["field"] == "priority":
            self.is_priority = True
            self.modifier = "priority"
            self.date = dateutil.parser.parse(data["date"])
            self.priority = metadata.get_priority(data["new_value"])
            self.text = data["field_info"]["priority_summary"]
            self.user = data["user"]
        elif data["field"] == "archived":
            self.is_archived = True
            self.date = dateutil.parser.parse(data["date"])
            self.archived = data["new_value"]
            self.user = data["user"]
            if self.archived:
                self.modifier = "archived"
                archived_reason_code = data["field_info"].get("archived_reason")
                if archived_reason_code:
                    self.archived_reason = ARCHIVED_REASON[archived_reason_code]

                self.archived_explanation = data["field_info"]["archived_explanation"]
            else:
                self.modifier = "unarchived"
                self.unarchived_reason = data["field_info"]["unarchived_reason"]
        else:
            self.is_assessment = True
            self.is_edit = data["old_value"] is not None
            self.name = metadata.get_assessment_name(data["field"])
            self.date = dateutil.parser.parse(data["date"])
            self.user = data["user"]


class Document(APIModel):
    """
    Wrapper around API document data
    """

    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.name = data["name"]
        self.size = data["size"]
        self.can_download = data["status"] == "virus_scanned"
        self.status = data["status"]

    @property
    def readable_status(self):
        return {
            "not_virus_scanned": "Not virus scanned",
            "virus_scanning_scheduled": "Virus scanning scheduled",
            "virus_scanning_in_progress": "Virus scanning in progress",
            "virus_scanning_failed": "Virus scanning failed.",
            "virus_scanned": "Virus scanned",
            "deletion_pending": "Deletion pending",
        }.get(self.status)
