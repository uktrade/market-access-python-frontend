import json
from operator import itemgetter

from utils.exceptions import HawkException

from django.conf import settings
from mohawk import Sender
import redis
import requests


UNFINISHED = '0'
OPEN_PENDING_ACTION = '1'
OPEN_IN_PROGRESS = '2'
RESOLVED_IN_PART = '3'
RESOLVED_IN_FULL = '4'
DORMANT = '5'
ARCHIVED = '6'
UNKNOWN = '7'


redis_client = redis.Redis.from_url(url=settings.REDIS_URI)


def get_metadata():
    metadata = redis_client.get('metadata')
    if metadata:
        return Metadata(json.loads(metadata))

    url = f'{settings.MARKET_ACCESS_API_URI}metadata'
    credentials = {
        "id": settings.MARKET_ACCESS_API_HAWK_ID,
        "key": settings.MARKET_ACCESS_API_HAWK_KEY,
        "algorithm": "sha256",
    }
    sender = Sender(
        credentials,
        url,
        'GET',
        content="",
        content_type="text/plain",
        always_hash_content=False,
    )

    response = requests.get(
        url,
        verify=not settings.DEBUG,
        headers={
            'Authorization': sender.request_header,
            'Content-Type': 'text/plain',
        }
    )

    if response.ok:
        metadata = response.json()
        redis_client.set(
            'metadata',
            json.dumps(metadata),
            ex=settings.METADATA_CACHE_TIME
        )
        return Metadata(metadata)

    raise HawkException("Call to fetch metadata failed")


class Metadata:
    STATUS_INFO = {
        '0': {
            'name': 'Unfinished',
            'modifier': 'unfinished',
            'hint': 'Barrier is unfinished'
        },
        '1': {
            'name': 'Pending',
            'modifier': 'assessment',
            'hint': 'Barrier is awaiting action'
        },
        '2': {
            'name': 'Open',
            'modifier': 'assessment',
            'hint': 'Barrier is being worked on'
        },
        '3': {
            'name': 'Part resolved',
            'modifier': 'resolved',
            'hint': (
                'Barrier impact has been significantly reduced but remains '
                'in part'
            )
        },
        '4': {
            'name': 'Resolved',
            'modifier': 'resolved',
            'hint': 'Barrier has been resolved for all UK companies'
         },
        '5': {
            'name': 'Paused',
            'modifier': 'hibernated',
            'hint': 'Barrier is present but not being pursued'
         },
        '6': {
            'name': 'Archived',
            'modifier': 'archived',
            'hint': 'Barrier is archived'
        },
        '7': {
            'name': 'Unknown',
            'modifier': 'hibernated',
            'hint': 'Barrier requires further work for the status to be known'
         },
    }

    def __init__(self, data):
        self.data = data

    def get_country(self, country_id):
        for country in self.data['countries']:
            if country['id'] == country_id:
                return country

    def get_country_list(self):
        return self.data['countries']

    def get_country_choices(self):
        countries = self.get_country_list()
        choices = (
            (country['id'], country['name'])
            for country in countries
        )
        return choices

    def get_admin_area(self, admin_area_id):
        for admin_area in self.data['country_admin_areas']:
            if (
                admin_area['id'] == admin_area_id
                and admin_area['disabled_on'] is None
            ):
                return admin_area

    def get_admin_areas(self, admin_area_ids):
        """
        Helper to get admin areas data in bulk.

        :param admin_area_ids: either a list or a comma separated string of UUIDs
        :return: GENERATOR - data of admin areas
        """
        area_ids = admin_area_ids or []
        if type(area_ids) == str:
            area_ids = admin_area_ids.replace(" ", "").split(",")
        admin_areas = (self.get_admin_area(area_id) for area_id in area_ids)
        return admin_areas

    def get_admin_area_choices(self, country_id):
        areas = self.get_admin_areas_by_country(country_id)
        choices = (
            (areas['id'], areas['name'])
            for areas in areas
        )
        return choices

    def get_admin_areas_by_country(self, country_id):
        return [
            admin_area
            for admin_area in self.data['country_admin_areas']
            if admin_area['country']['id'] == country_id
        ]

    def get_sector(self, sector_id):
        for sector in self.data.get('sectors', []):
            if sector['id'] == sector_id:
                return sector

    def get_sectors_by_ids(self, sector_ids):
        return [
            sector
            for sector in self.data.get('sectors', [])
            if sector['id'] in sector_ids
        ]

    def get_sector_list(self, level=None):
        if level is not None:
            return [
                sector
                for sector in self.data['sectors']
                if sector['level'] == level
            ]
        return self.data['sectors']

    def get_status(self, status_id):
        for id, name in self.data['barrier_status'].items():
            self.STATUS_INFO[id]['id'] = id
            self.STATUS_INFO[id]['name'] = name

        return self.STATUS_INFO[status_id]

    def get_problem_status(self, problem_status_id):
        status_types = self.data['status_types']
        status_types.update({
            '1': 'A procedural, short-term barrier',
            '2': 'A long-term strategic barrier',
        })
        return status_types.get(str(problem_status_id))

    def get_location(self, country, admin_areas):
        country_data = self.get_country(country)

        if country_data:
            country_name = country_data['name']
        else:
            country_name = ""

        if admin_areas:
            admin_areas_string = ", ".join([
                self.get_admin_area(admin_area)['name']
                for admin_area in admin_areas
            ])
            return f"{admin_areas_string} ({country_name})"

        return country_name

    def get_eu_exit_related_text(self, code):
        return self.data['adv_boolean'].get(str(code), 'Unknown')

    def get_source(self, source):
        return self.data['barrier_source'].get(source)

    def get_sub_status(self, sub_status):
        return self.data['barrier_pending'].get(sub_status)

    def get_status_type(self, id, field_info=None):
        if id in self.STATUS_INFO.keys():
            name = self.get_status(id)['name']
            if field_info and id == '1':
                sub_status = self.get_sub_status_text(field_info)
                return f"{name}{sub_status}"
            return name

        return id

    def get_sub_status_text(self, field_info):
        if field_info['sub_status'] == "OTHER":
            sub_status = field_info['sub_status_other']
        else:
            sub_status = self.get_sub_status(field_info['sub_status'])

        return f" ({sub_status})"

    def get_priority(self, priority_code):
        if priority_code == 'None':
            priority_code = 'UNKNOWN'

        for priority in self.data['barrier_priorities']:
            if priority['code'] == priority_code:
                return priority

    def get_assessment_name(self, assessment_code):
        assessment_names = {
            'impact': 'Economic assessment',
            'value_to_economy': 'Value to UK Economy',
            'import_market_size': 'Import Market Size',
            'export_value': 'Value of currently affected UK exports',
            'commercial_value': 'Commercial Value',
        }
        return assessment_names.get(assessment_code)

    def get_barrier_type_list(self, sort=True):
        """
        Dedupe and sort the barrier types
        """
        ids = []
        unique_barrier_types = []
        for barrier_type in self.data.get('barrier_types'):
            if barrier_type['id'] not in ids:
                unique_barrier_types.append(barrier_type)
                ids.append(barrier_type['id'])

        if sort:
            unique_barrier_types.sort(key=itemgetter('title'))
        return unique_barrier_types

    def get_barrier_type(self, type_id):
        for barrier_type in self.data['barrier_types']:
            if str(barrier_type['id']) == str(type_id):
                return barrier_type

    def get_overseas_region_list(self):
        return [
            country['overseas_region']
            for country in self.get_country_list()
            if country['disabled_on'] is None
            and country.get('overseas_region') is not None
        ]

    def get_impact_text(self, impact_code):
        return self.data.get('assessment_impact', {}).get(impact_code)

    def get_barrier_types_by_category(self, category):
        return [
            barrier_type
            for barrier_type in self.get_barrier_type_list(sort=False)
            if barrier_type['category'] == category
        ]

    def get_goods(self):
        return self.get_barrier_types_by_category("GOODS")

    def get_services(self):
        return self.get_barrier_types_by_category("SERVICES")

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
