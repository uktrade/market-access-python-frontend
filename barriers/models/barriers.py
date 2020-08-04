from barriers.constants import ARCHIVED_REASON, PUBLIC_BARRIER_STATUSES
from barriers.models.commodities import BarrierCommodity
from barriers.models.wto import WTOProfile

from utils.metadata import get_metadata
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
    _public_barrier = None
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
        return [admin_area["id"] for admin_area in self.data.get("admin_areas", [])]

    @property
    def archived_on(self):
        return dateutil.parser.parse(self.data["archived_on"])

    @property
    def archived_reason(self):
        return ARCHIVED_REASON[self.data["archived_reason"]]

    @property
    def category_titles(self):
        return [category["title"] for category in self.categories]

    @property
    def created_on(self):
        return dateutil.parser.parse(self.data["created_on"])

    @property
    def end_date(self):
        if self.data.get("end_date"):
            return dateutil.parser.parse(self.data["end_date"])

    @property
    def commodities(self):
        return [BarrierCommodity(commodity) for commodity in self.data.get("commodities", [])]

    @property
    def commodities_grouped_by_country(self):
        grouped_commodities = {}
        for barrier_commodity in self.commodities:
            grouped_commodities.setdefault(barrier_commodity.country["id"], [])
            grouped_commodities[barrier_commodity.country["id"]].append(barrier_commodity)
        return grouped_commodities

    @property
    def last_seen_on(self):
        return dateutil.parser.parse(self.data["last_seen_on"])

    def get_location_text(self):
        if not self.country:
            return ""

        country_name = self.country.get("name", "")

        if self.admin_areas:
            admin_areas_string = ", ".join(
                [admin_area.get("name", "") for admin_area in self.admin_areas]
            )
            return f"{admin_areas_string} ({country_name})"

        return country_name

    @property
    def location(self):
        if self._location is None:
            self._location = self.get_location_text()
        return self._location

    @property
    def modified_on(self):
        return dateutil.parser.parse(self.data["modified_on"])

    @property
    def public_barrier(self):
        if self._public_barrier is None and self.data.get("public_barrier"):
            self._public_barrier = PublicBarrier(self.data.get("public_barrier"))
        return self._public_barrier

    @property
    def problem_status_text(self):
        return self.metadata.get_problem_status(self.data["problem_status"])

    @property
    def created_on(self):
        return dateutil.parser.parse(self.data["created_on"])

    @property
    def reported_by(self):
        return self.created_by

    @property
    def reported_on(self):
        return self.created_on

    @property
    def sector_ids(self):
        return [sector["id"] for sector in self.data.get("sectors", [])]

    @property
    def sector_names(self):
        if self.all_sectors:
            return ["All sectors"]
        if self.sectors:
            return [sector.get("name", "Unknown") for sector in self.sectors]
        return []

    @property
    def status(self):
        if self._status is None:
            self.data["status"]["id"] = str(self.data["status"]["id"])
            self._status = self.metadata.get_status(self.data["status"]["id"])
            self._status.update(self.data["status"])
        return self._status

    @property
    def status_date(self):
        return dateutil.parser.parse(self.data.get("status_date"))

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
    _internal_country = None
    _internal_sectors = None
    _internal_status = None
    _metadata = None
    _sectors = None
    _status = None

    @property
    def any_internal_sectors_changed(self):
        return (
            self.data.get("internal_sectors_changed")
            or self.data.get("internal_all_sectors_changed")
        )

    @property
    def category_titles(self):
        return [category["title"] for category in self.categories]

    @property
    def internal_categories(self):
        return self.data.get("internal_categories", [])

    @property
    def internal_category_titles(self):
        return [category["title"] for category in self.internal_categories]

    @property
    def first_published_on(self):
        if self.data.get("first_published_on") is not None:
            return dateutil.parser.parse(self.data["first_published_on"])

    @property
    def last_published_on(self):
        if self.data.get("last_published_on") is not None:
            return dateutil.parser.parse(self.data["last_published_on"])

    @property
    def unpublished_changes(self):
        if self.data.get("last_published_on") is None:
            return False
        return self.data.get("unpublished_changes")

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
    def latest_published_version(self):
        if self.data.get("latest_published_version") is not None:
            return PublicBarrier(self.data["latest_published_version"])

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
    def internal_all_sectors(self):
        return self.data.get("internal_all_sectors")

    @property
    def internal_sectors(self):
        return self.data.get("internal_sectors", [])

    @property
    def internal_sector_names(self):
        if self.internal_all_sectors:
            return ["All sectors"]
        if self.internal_sectors:
            return [sector.get("name", "Unknown") for sector in self.internal_sectors]
        return []

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
