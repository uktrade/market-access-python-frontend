import json

from django.conf import settings

import redis


def get_metadata():
    r = redis.Redis(host='localhost', port=6379, db=0)
    metadata = r.get('metadata')
    if metadata:
        return Metadata(json.loads(metadata))

    # TODO: Fix circular import
    from utils.api_client import MarketAccessAPIClient
    client = MarketAccessAPIClient()
    metadata = client.get('metadata')
    r.set('metadata', json.dumps(metadata), ex=settings.METADATA_CACHE_TIME)
    return Metadata(metadata)


class Metadata:
    STATUS_INFO = {
        '0': { 'name': 'Unfinished', 'modifier': 'unfinished', 'hint': 'Barrier is unfinished' },
        '1': { 'name': 'Pending', 'modifier': 'assessment', 'hint': 'Barrier is awaiting action' },
        '2': { 'name': 'Open', 'modifier': 'assessment', 'hint': 'Barrier is being worked on' },
        '3': { 'name': 'Part resolved', 'modifier': 'resolved', 'hint': 'Barrier impact has been significantly reduced but remains in part' },
        '4': { 'name': 'Resolved', 'modifier': 'resolved', 'hint': 'Barrier has been resolved for all UK companies' },
        '5': { 'name': 'Paused', 'modifier': 'hibernated', 'hint': 'Barrier is present but not being pursued' },
        '6': { 'name': 'Archived', 'modifier': 'archived', 'hint': 'Barrier is archived' },
        '7': { 'name': 'Unknown', 'modifier': 'hibernated', 'hint': 'Barrier requires further work for the status to be known' },
    }
    def __init__(self, data):
        self.data = data

    def get_country(self, country_id):
        for country in self.data['countries']:
            if country['id'] == country_id:
                return country

    def get_admin_area(self, admin_area_id):
        for admin_area in self.data['country_admin_areas']:
            if admin_area['id'] == admin_area_id:
                return admin_area

    def get_sector(self, sector_id):
        for sector in self.data.get('sectors', []):
            if sector['id'] == sector_id:
                return sector

    def get_status(self, status_id):
        for id, name in self.data['barrier_status'].items():
            self.STATUS_INFO[id]['name'] = name

        return self.STATUS_INFO[status_id]

    def get_location(self, country, admin_areas):
        country_data = self.get_country(country)

        if country_data:
            country_name = country_data['name']
        else:
            country_name = ""

        if admin_areas:
            admin_areas_string = ", ".join(
                [self.get_admin_area(admin_area)['name'] for admin_area in admin_areas]
            )
            return f"{admin_areas_string} ({country_name})"

        return country_name
