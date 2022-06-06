import dateutil.parser

from barriers.constants import PUBLIC_BARRIER_STATUSES
from barriers.models.assessments import (
    EconomicAssessment,
    EconomicImpactAssessment,
    ResolvabilityAssessment,
    StrategicAssessment,
)
from barriers.models.commodities import BarrierCommodity
from barriers.models.wto import WTOProfile
from utils.metadata import get_metadata
from utils.models import APIModel


class Barrier(APIModel):
    """
    Wrapper around API barrier data
    """

    _admin_areas = None
    _country = None
    _location = None
    _metadata = None
    _public_barrier = None
    _economic_assessments = None
    _economic_impact_assessments = None
    _resolvability_assessments = None
    _strategic_assessments = None
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
    def category_titles(self):
        return [category["title"] for category in self.categories]

    @property
    def created_on(self):
        return dateutil.parser.parse(self.data["created_on"])

    @property
    def estimated_resolution_date(self):
        if self.data.get("estimated_resolution_date"):
            return dateutil.parser.parse(self.data["estimated_resolution_date"])

    @property
    def commodities(self):
        return [
            BarrierCommodity(commodity)
            for commodity in self.data.get("commodities", [])
        ]

    @property
    def public_eligibility(self):
        return self.data.get("public_eligibility")

    @property
    def public_eligibility_postponed(self):
        return self.data.get("public_eligibility_postponed")

    @property
    def top_priority_status(self):
        return self.data.get("top_priority_status")

    @property
    def commodities_grouped_by_country(self):
        grouped_commodities = {}
        for barrier_commodity in self.commodities:
            if barrier_commodity.country:
                key = barrier_commodity.country["id"]
            elif barrier_commodity.trading_bloc:
                key = barrier_commodity.trading_bloc["code"]

            grouped_commodities.setdefault(key, [])
            grouped_commodities[key].append(barrier_commodity)
        return grouped_commodities

    @property
    def last_seen_on(self):
        return dateutil.parser.parse(self.data["last_seen_on"])

    @property
    def location(self):
        return self.data.get("location")

    @property
    def modified_on(self):
        return dateutil.parser.parse(self.data["modified_on"])

    @property
    def public_barrier(self):
        if self._public_barrier is None and self.data.get("public_barrier"):
            self._public_barrier = PublicBarrier(self.data.get("public_barrier"))
        return self._public_barrier

    @property
    def reported_by(self):
        return self.created_by

    @property
    def reported_on(self):
        return self.created_on

    @property
    def archived_economic_assessments(self):
        return [
            assessment
            for assessment in self.economic_assessments
            if assessment.archived is True
        ]

    @property
    def current_economic_assessment(self):
        for assessment in self.economic_assessments:
            if assessment.archived is False:
                return assessment

    @property
    def economic_assessments(self):
        if self._economic_assessments is None:
            self._economic_assessments = [
                EconomicAssessment(assessment)
                for assessment in self.data.get("economic_assessments", [])
            ]
        return self._economic_assessments

    @property
    def archived_economic_impact_assessments(self):
        return [
            assessment
            for assessment in self.economic_impact_assessments
            if assessment.archived is True
        ]

    @property
    def current_economic_impact_assessment(self):
        for assessment in self.economic_impact_assessments:
            if assessment.archived is False:
                return assessment

    @property
    def economic_impact_assessments(self):
        if self._economic_impact_assessments is None:
            self._economic_impact_assessments = [
                EconomicImpactAssessment(assessment)
                for assessment in self.data.get("valuation_assessments", [])
            ]
        return self._economic_impact_assessments

    @property
    def archived_resolvability_assessments(self):
        return [
            assessment
            for assessment in self.resolvability_assessments
            if assessment.archived is True
        ]

    @property
    def current_resolvability_assessment(self):
        for assessment in self.resolvability_assessments:
            if assessment.archived is False:
                return assessment

    @property
    def resolvability_assessments(self):
        if self._resolvability_assessments is None:
            self._resolvability_assessments = [
                ResolvabilityAssessment(assessment)
                for assessment in self.data.get("resolvability_assessments", [])
            ]
        return self._resolvability_assessments

    @property
    def archived_strategic_assessments(self):
        return [
            assessment
            for assessment in self.strategic_assessments
            if assessment.archived is True
        ]

    @property
    def current_strategic_assessment(self):
        for assessment in self.strategic_assessments:
            if assessment.archived is False:
                return assessment

    @property
    def strategic_assessments(self):
        if self._strategic_assessments is None:
            self._strategic_assessments = [
                StrategicAssessment(assessment)
                for assessment in self.data.get("strategic_assessments", [])
            ]
        return self._strategic_assessments

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
        return sorted(tags, key=lambda k: k["order"])

    @property
    def government_organisations(self):
        return self.data.get("government_organisations") or ()

    @property
    def government_organisations_names(self):
        org_names = []
        for org in self.government_organisations():
            org_names.append(org["name"])
        return org_names

    @property
    def government_organisation_ids_as_str(self):
        return ",".join((str(org["id"]) for org in self.government_organisations))

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

    @property
    def progress_status(self):
        return self.data.get("progress_status")

    @property
    def progress_update(self):
        return self.data.get("progress_update")

    @property
    def next_steps(self):
        return self.data.get("next_steps")

    @property
    def progress_updates(self):
        return self.data.get("progress_updates")

    @property
    def latest_progress_update(self):
        if self.progress_updates:
            return self.progress_updates[0]
        return None


class PublicBarrier(APIModel):
    _country = None
    _internal_country = None
    _internal_sectors = None
    _internal_status = None
    _metadata = None
    _sectors = None
    _status = None

    @property
    def internal_code(self):
        return self.data.get("internal_code")

    @property
    def internal_id(self):
        return self.data.get("internal_id")

    @property
    def any_internal_sectors_changed(self):
        return self.data.get("internal_sectors_changed") or self.data.get(
            "internal_all_sectors_changed"
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
    def internal_is_resolved(self):
        return self.data.get("internal_is_resolved")

    @property
    def internal_status_date(self):
        if self.data.get("internal_status_date"):
            return dateutil.parser.parse(self.data["internal_status_date"])

    @property
    def internal_government_organisations(self):
        return self.data.get("internal_government_organisations", [])

    @property
    def internal_government_organisations_names(self):
        return [org["name"] for org in self.internal_government_organisations]

    @property
    def is_resolved_text(self):
        return self.get_resolved_text(self.is_resolved, self.status_date)

    @property
    def internal_is_resolved_text(self):
        return self.get_resolved_text(
            self.internal_is_resolved, self.internal_status_date
        )

    def get_resolved_text(self, is_resolved, status_date):
        if is_resolved:
            if status_date:
                return f"Yes - {status_date.strftime('%B %Y')}"
            return "Yes"
        return "No"

    @property
    def status_date(self):
        if self.data.get("status_date"):
            return dateutil.parser.parse(self.data["status_date"])

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
    def public_id(self):
        return f"PID-{self.id}"

    @property
    def public_status_text(self):
        return {
            PUBLIC_BARRIER_STATUSES.UNKNOWN: "To be decided",
            PUBLIC_BARRIER_STATUSES.INELIGIBLE: "Not allowed",
            PUBLIC_BARRIER_STATUSES.ELIGIBLE: "Quality assurance - awaiting approval",
            PUBLIC_BARRIER_STATUSES.READY: "Ready to publish",
            PUBLIC_BARRIER_STATUSES.PUBLISHED: "Published",
            PUBLIC_BARRIER_STATUSES.UNPUBLISHED: "Unpublished",
            PUBLIC_BARRIER_STATUSES.REVIEW_LATER: "Review later",
        }.get(self.public_view_status)

    @property
    def ready_text(self):
        return {
            PUBLIC_BARRIER_STATUSES.UNKNOWN: "Not ready to publish",
            PUBLIC_BARRIER_STATUSES.INELIGIBLE: "",
            PUBLIC_BARRIER_STATUSES.ELIGIBLE: "Not ready to publish",
            PUBLIC_BARRIER_STATUSES.READY: "Quality assurance complete",
            PUBLIC_BARRIER_STATUSES.PUBLISHED: "",
            PUBLIC_BARRIER_STATUSES.UNPUBLISHED: "",
            PUBLIC_BARRIER_STATUSES.REVIEW_LATER: "Review later",
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
    def internal_any_sectors_changed(self):
        return self.internal_sectors_changed or self.internal_all_sectors_changed

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
            return "Quality assurance"
        elif self.public_view_status == PUBLIC_BARRIER_STATUSES.READY:
            return "Ready to publish"
        elif self.public_view_status == PUBLIC_BARRIER_STATUSES.PUBLISHED:
            return "Published"

    @property
    def reported_on(self):
        if self.data.get("reported_on"):
            return dateutil.parser.parse(self.data["reported_on"])

    @property
    def light_touch_reviews(self):
        return self.data.get("light_touch_reviews")

    @property
    def awaiting_reviews_from(self):
        from_who = []
        if not self.light_touch_reviews["content_team_approval"]:
            from_who.append("Content")
        if (
            self.light_touch_reviews["hm_trade_commissioner_approval_enabled"]
            and not self.light_touch_reviews["hm_trade_commissioner_approval"]
        ):
            from_who.append("HM Trade Commissioner")
        from_who += [
            org["name"]
            for org in self.internal_government_organisations
            if not (
                int(org["id"])
                in self.light_touch_reviews["government_organisation_approvals"]
            )
        ]
        return from_who
