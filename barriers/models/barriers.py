from barriers.constants import ARCHIVED_REASON, PUBLIC_BARRIER_STATUSES
from barriers.models.wto import WTOProfile

from utils.metadata import get_metadata
from utils.models import APIModel

import dateutil.parser


class Barrier(APIModel):
    """
    Wrapper around API barrier data
    """

    _admin_areas = None
    _categories = None
    _country = None
    _location = None
    _metadata = None
    _sectors = None
    _status = None
    _wto_profile = None

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
    def categories(self):
        if self._categories is None:
            self._categories = [
                self.metadata.get_category(category)
                for category in self.data.get("categories", [])
            ]
        return self._categories

    @property
    def category_titles(self):
        return [category["title"] for category in self.categories]

    @property
    def country(self):
        if self._country is None and self.export_country:
            self._country = self.metadata.get_country(self.export_country)
        return self._country

    @property
    def created_on(self):
        return dateutil.parser.parse(self.data["created_on"])

    @property
    def end_date(self):
        if self.data.get("end_date"):
            return dateutil.parser.parse(self.data["end_date"])

    @property
    def eu_exit_related_text(self):
        return self.metadata.get_eu_exit_related_text(self.eu_exit_related)

    @property
    def last_seen_on(self):
        return dateutil.parser.parse(self.data["last_seen_on"])

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
        if self.all_sectors:
            return ["All sectors"]
        if self.sectors:
            return [sector.get("name", "Unknown") for sector in self.sectors]
        return []

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
    def tags(self):
        tags = self.data.get("tags") or ()
        return sorted(tags, key=lambda k: k['order'])

    @property
    def trade_direction(self):
        return str(self.data.get("trade_direction"))

    @property
    def trade_direction_text(self):
        return self.metadata.get_trade_direction(self.trade_direction)

    @property
    def title(self):
        return self.barrier_title

    @property
    def wto_profile(self):
        if self._wto_profile is None:
            if self.data.get("wto_profile") is not None:
                self._wto_profile = WTOProfile(self.data.get("wto_profile"))
        return self._wto_profile

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


class PublicBarrier(APIModel):
    _country = None
    _metadata = None
    _sectors = None
    _status = None

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = get_metadata()
        return self._metadata

    @property
    def country(self):
        if self._country is None and self.data.get("country"):
            country_id = self.data.get("country")
            self._country = self.metadata.get_country(country_id)
        return self._country

    @property
    def first_published_on(self):
        if self.data.get("first_published_on") is not None:
            return dateutil.parser.parse(self.data["first_published_on"])

    @property
    def last_published_on(self):
        if self.data.get("last_published_on") is not None:
            return dateutil.parser.parse(self.data["last_published_on"])

    @property
    def unpublished_on(self):
        if self.data.get("unpublished_on") is not None:
            return dateutil.parser.parse(self.data["unpublished_on"])

    @property
    def is_eligible(self):
        return self.public_view_status == PUBLIC_BARRIER_STATUSES.ELIGIBLE

    @property
    def is_published(self):
        return self.public_view_status == PUBLIC_BARRIER_STATUSES.PUBLISHED

    @property
    def is_ready(self):
        return self.public_view_status == PUBLIC_BARRIER_STATUSES.READY

    @property
    def is_unpublished(self):
        return self.public_view_status == PUBLIC_BARRIER_STATUSES.UNPUBLISHED

    @property
    def public_status_text(self):
        return {
            PUBLIC_BARRIER_STATUSES.UNKNOWN: "To be decided",
            PUBLIC_BARRIER_STATUSES.INELIGIBLE: "Not for public view",
            PUBLIC_BARRIER_STATUSES.ELIGIBLE: "Allowed - yet to be published",
            PUBLIC_BARRIER_STATUSES.READY: "Allowed - yet to be published",
            PUBLIC_BARRIER_STATUSES.PUBLISHED: "Published",
            PUBLIC_BARRIER_STATUSES.UNPUBLISHED: "Unpublished",
        }.get(self.public_view_status)

    @property
    def ready_text(self):
        return {
            PUBLIC_BARRIER_STATUSES.UNKNOWN: "Not ready to publish",
            PUBLIC_BARRIER_STATUSES.INELIGIBLE: "",
            PUBLIC_BARRIER_STATUSES.ELIGIBLE: "Not ready to publish",
            PUBLIC_BARRIER_STATUSES.READY: "Ready to publish",
            PUBLIC_BARRIER_STATUSES.PUBLISHED: "",
            PUBLIC_BARRIER_STATUSES.UNPUBLISHED: "",
        }.get(self.public_view_status)

    @property
    def status(self):
        if self._status is None:
            status_id = str(self.data["status"])
            self._status = self.metadata.get_status(status_id)
        return self._status

    @property
    def sectors(self):
        if self._sectors is None:
            self._sectors = [
                self.metadata.get_sector(sector_id) for sector_id in self.data.get("sectors")
            ]
        return self._sectors

    @property
    def sector_names(self):
        if self.all_sectors:
            return ["All sectors"]
        if self.sectors:
            return [sector.get("name", "Unknown") for sector in self.sectors]
        return []

    @property
    def tab_badge(self):
        if self.public_view_status == PUBLIC_BARRIER_STATUSES.ELIGIBLE:
            return "Eligible"
        elif self.public_view_status == PUBLIC_BARRIER_STATUSES.READY:
            return "Ready"
        elif self.public_view_status == PUBLIC_BARRIER_STATUSES.PUBLISHED:
            return "Published"
