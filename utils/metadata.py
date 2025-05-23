import json
from operator import itemgetter

import redis
import requests
from django.conf import settings
from mohawk import Sender

from barriers.constants import DEPRECATED_TAGS, Statuses
from core.filecache import memfiles
from utils.exceptions import HawkException

if settings.DJANGO_ENV == "test":
    redis_client = None
else:
    redis_client = redis.Redis.from_url(url=settings.REDIS_URI)


def get_metadata():
    if settings.DJANGO_ENV == "test":
        # we're testing and have no access to the API, so use the fixture.
        file = f"{settings.BASE_DIR}/../core/fixtures/metadata.json"
        return Metadata(json.loads(memfiles.open(file)))

    metadata = redis_client.get("metadata")
    if metadata:
        return Metadata(json.loads(metadata))

    url = f"{settings.MARKET_ACCESS_API_URI}metadata"
    sender = Sender(
        settings.MARKET_ACCESS_API_HAWK_CREDS,
        url,
        "GET",
        content="",
        content_type="text/plain",
        always_hash_content=False,
    )

    response = requests.get(
        url,
        verify=not settings.DEBUG,
        headers={
            "Authorization": sender.request_header,
            "Content-Type": "text/plain",
        },
    )

    if not response.ok:
        raise HawkException(f"Call to fetch metadata failed {response}")

    metadata = response.json()
    redis_client.set("metadata", json.dumps(metadata), ex=settings.METADATA_CACHE_TIME)
    return Metadata(metadata)


class Metadata:
    """
    Wrapper around the raw metadata with helper functions
    """

    STATUS_INFO = {
        Statuses.UNFINISHED: {
            "name": "Unfinished",
            "modifier": "unfinished",
            "hint": "Barrier is unfinished",
        },
        Statuses.OPEN_IN_PROGRESS: {
            "name": "Open",
            "modifier": "open-in-progress",
            "hint": "Barrier is being worked on",
        },
        Statuses.RESOLVED_IN_PART: {
            "name": "Part resolved",
            "modifier": "resolved",
            "hint": "Barrier impact has been significantly reduced but remains in part",
        },
        Statuses.RESOLVED_IN_FULL: {
            "name": "Resolved",
            "modifier": "resolved",
            "hint": "Barrier has been resolved for all UK companies",
        },
        Statuses.DORMANT: {
            "name": "Paused",
            "modifier": "hibernated",
            "hint": "Barrier is present but not being pursued",
        },
        Statuses.ARCHIVED: {
            "name": "Archived",
            "modifier": "archived",
            "hint": "Barrier is archived",
        },
        Statuses.UNKNOWN: {
            "name": "Unknown",
            "modifier": "unknown",
            "hint": "Barrier requires further work for the status to be known",
        },
    }

    def __init__(self, data):
        self.data = data

    def get_admin_area_list(self):
        return self.data["admin_areas"]

    def get_admin_area(self, admin_area_id):
        for admin_area in self.data["admin_areas"]:
            if admin_area["id"] == admin_area_id and admin_area["disabled_on"] is None:
                return admin_area

    def get_admin_areas(self, admin_area_ids):
        """
        Helper to get admin areas data in bulk.

        :param admin_area_ids: either a list or a comma separated string of UUIDs
        :return: GENERATOR - data of admin areas
        """
        area_ids = admin_area_ids or []
        if isinstance(area_ids, str):
            area_ids = admin_area_ids.replace(" ", "").split(",")
        admin_areas = [self.get_admin_area(area_id) for area_id in area_ids]
        return admin_areas

    def get_admin_areas_by_country(self, country_id):
        return [
            admin_area
            for admin_area in self.data["admin_areas"]
            if admin_area["country"]["id"] == country_id
        ]

    def get_countries_with_admin_areas_list(self):
        countries_list = []
        results_list = []
        for admin_area in self.data["admin_areas"]:
            if admin_area["country"]["id"] not in countries_list:
                countries_list.append(admin_area["country"]["id"])
                results_list.append(
                    {
                        "id": admin_area["country"]["id"],
                        "name": admin_area["country"]["name"],
                    }
                )
        return results_list

    def get_country(self, country_id):
        for country in self.data["countries"]:
            if country["id"] == country_id:
                return country

    def get_country_list(self):
        return self.data["countries"]

    def get_country_choices(self):
        return [(country["id"], country["name"]) for country in self.get_country_list()]

    def get_overseas_region_list(self):
        self.data["overseas_regions"].sort(key=itemgetter("name"))
        return self.data["overseas_regions"]

    def get_overseas_region_by_id(self, region_id):
        for region in self.get_overseas_region_list():
            if region["id"] == str(region_id):
                return region
        return None

    def get_overseas_region_choices(self):
        return [
            (region["id"], region["name"]) for region in self.get_overseas_region_list()
        ]

    def get_sector(self, sector_id):
        for sector in self.data.get("sectors", []):
            if sector["id"] == sector_id:
                return sector

    def get_sectors(self, sector_ids):
        """
        Helper to get sectors data in bulk.

        :param sector_ids: either a list or a comma separated string of UUIDs
        :return: GENERATOR - data of sectors
        """
        sec_ids = sector_ids or []
        if isinstance(sec_ids, str):
            sec_ids = sector_ids.replace(" ", "").split(",")
        sectors = (self.get_sector(sector_id) for sector_id in sec_ids)
        return sectors

    def get_sectors_by_ids(self, sector_ids):
        return [
            sector
            for sector in self.data.get("sectors", [])
            if sector["id"] in sector_ids and sector["disabled_on"] is None
        ]

    def get_sector_list(self, level=None):
        return [
            sector
            for sector in self.data["sectors"]
            if (level is None or sector["level"] == level)
            and sector["disabled_on"] is None
        ]

    def get_sector_choices(self, level=None):
        return [
            (sector["id"], sector["name"]) for sector in self.get_sector_list(level)
        ]

    def get_status(self, status_id):
        for id, name in self.data["barrier_status"].items():
            if id == "1":
                continue
            self.STATUS_INFO[id]["id"] = id
            self.STATUS_INFO[id]["name"] = name

        return self.STATUS_INFO[status_id]

    def get_status_text(
        self,
        status_id,
        sub_status=None,
        sub_status_other=None,
    ):
        if status_id in self.STATUS_INFO.keys():
            return self.get_status(status_id)["name"]
        return status_id

    def get_status_choices(self):
        return [
            (status[0], status[1]) for status in self.data["barrier_status"].items()
        ]

    def get_sub_status_text(self, sub_status, sub_status_other=None):
        if sub_status == "OTHER":
            return sub_status_other

        return self.data["barrier_pending"].get(sub_status)

    def get_term(self, term_id):
        terms = self.data["barrier_terms"]
        return terms.get(str(term_id))

    def get_source(self, source):
        return self.data["barrier_source"].get(source)

    def get_priority(self, priority_code):
        if priority_code == "None":
            priority_code = "UNKNOWN"

        for priority in self.data["barrier_priorities"]:
            if priority["code"] == priority_code:
                return priority

    def get_policy_team_list(self, sort=True):
        """
        Dedupe and sort the policy teams
        """
        ids = []
        unique_policy_teams = []
        for policy_team in self.data.get("policy_teams"):
            if policy_team["id"] not in ids:
                unique_policy_teams.append(policy_team)
                ids.append(policy_team["id"])

        if sort:
            unique_policy_teams.sort(key=itemgetter("title"))

        return unique_policy_teams

    def get_policy_team(self, policy_team_id):
        for policy_team in self.data["policy_teams"]:
            if str(policy_team["id"]) == str(policy_team_id):
                return policy_team

    def get_economic_assessment_impact(self):
        return self.data.get("economic_assessment_impact", {})

    def get_economic_assessment_rating(self):
        return self.data.get("economic_assessment_rating", {})

    def get_resolvability_assessment_effort(self):
        return self.data.get("resolvability_assessment_effort", {})

    def get_resolvability_assessment_time(self):
        return self.data.get("resolvability_assessment_time", {})

    def get_strategic_assessment_scale(self):
        return self.data.get("strategic_assessment_scale", {})

    def get_report_stages(self):
        stages = self.data.get("report_stages", {})
        # filter out "Add a barrier" as that's not a valid stage
        exclude_stages = ("Add a barrier",)
        remove_keys = []
        for key, value in stages.items():
            if value in exclude_stages:
                remove_keys.append(key)

        for key in remove_keys:
            stages.pop(key)

        return stages

    def get_barrier_tag(self, tag_id):
        for tag in self.get_barrier_tags():
            if str(tag["id"]) == str(tag_id):
                return tag
        return {
            "id": tag_id,
            "title": "[unknown tag]",
            "description": "No such tag exists",
            "show_at_reporting": False,
            "order": 9999,
        }

    def get_barrier_tags(self):
        tags = self.data.get("barrier_tags", [])
        return sorted(tags, key=lambda k: k["order"])

    def get_barrier_tag_choices(self, list_use):
        """
        Generates tag choices for edit or search tags pages.
        Includes all tags except Top Priority, as that is assigned seperately.
        """

        tag_list = self.get_barrier_tags()

        if list_use == "edit":
            # If this list is for the edit pages, return as generator
            return ((tag["id"], tag["title"], tag["description"]) for tag in tag_list)
        elif list_use == "search":
            # If this list is for the search functionality, return as a plain list
            return tag_list

    def get_report_tag_choices(self):
        """
        Generates tag choices.
        Only returns a subset of tags when reporting a barrier.
        """
        return (
            (tag["id"], tag["title"], tag["description"])
            for tag in self.get_barrier_tags()
            if tag["show_at_reporting"] is True and tag["title"] not in DEPRECATED_TAGS
        )

    def get_trade_categories(self):
        return self.data.get("trade_categories", {})

    def get_trade_direction(self, key=None, all_items=False):
        """
        Helper to get either a value or all items for trade_direction.

        :param key:         STR  - dict key
        :param all_items:   BOOL
        :return: Returns either all items in the dict or the value of a specific key
        """
        trade_directions = self.data.get("trade_direction", {})
        if all_items:
            return trade_directions.items()
        else:
            return trade_directions.get(key)

    def get_trade_direction_choices(self):
        return (td for td in self.get_trade_direction(all_items=True))

    def get_trading_bloc(self, code):
        for trading_bloc in self.get_trading_bloc_list():
            if trading_bloc["code"] == code:
                return trading_bloc

    def get_trading_bloc_list(self):
        return self.data.get("trading_blocs", [])

    def get_trading_bloc_by_country_id(self, country_id):
        for trading_bloc in self.get_trading_bloc_list():
            if country_id in trading_bloc["country_ids"]:
                return {
                    "code": trading_bloc["code"],
                    "name": trading_bloc["name"],
                    "short_name": trading_bloc["short_name"],
                }

    def is_trading_bloc_code(self, code):
        return self.get_trading_bloc(code) is not None

    def get_wto_committee_groups(self):
        return self.data.get("wto_committee_groups", [])

    def get_gov_organisations(self):
        return self.data.get("government_organisations", [])

    def get_gov_organisation_choices(self):
        """
        Generates government organisation choices.
        """
        return ((str(org["id"]), org["name"]) for org in self.get_gov_organisations())

    def get_gov_organisation_dict(self):
        return dict(self.get_gov_organisation_choices())

    def get_government_organisation(self, org_id):
        for org in self.get_gov_organisations():
            if str(org["id"]) == str(org_id):
                return org

    def get_gov_organisations_by_ids(self, list_of_ids):
        list_of_ids = [str(id) for id in list_of_ids]
        return (
            org for org in self.get_gov_organisations() if str(org["id"]) in list_of_ids
        )

    def get_top_priority_status(self, status):
        for status in self.data["top_priority_status"]:
            if str(status["id"]) == str(status):
                return status

    def get_search_ordering_choices(self):
        return self.data["search_ordering_choices"]


class MetadataMixin:
    _metadata = None

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = get_metadata()
        return self._metadata
