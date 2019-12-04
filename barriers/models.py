import dateutil.parser

from django.db import models

from utils.metadata import get_metadata


class Barrier:
    def __init__(self, data):
        metadata = get_metadata()
        self.id = data['id']
        self.code = data['code']
        self.title = data['barrier_title']

        # TODO: Fix these
        self.is_open = (data['status']['id'] == "OPEN")
        self.is_resolved = (data['status']['id'] == "RESOLVED")
        self.is_hibernated = (data['status']['id'] == "HIBERNATED")

        self.location = metadata.get_location(data['export_country'], data['country_admin_areas'])

        if data.get('sectors'):
            self.sectors = [metadata.get_sector(sector_id) for sector_id in data['sectors']]
        else:
            self.sectors = []

        self.sector_names = [sector['name'] for sector in self.sectors]

        status_code = str(data['status']['id'])
        self.status = metadata.get_status(status_code)
        self.priority = data['priority']
        self.date = {
            'reported': dateutil.parser.parse(data['reported_on']),
            'status': dateutil.parser.parse(data['status']['date']),
            'created': dateutil.parser.parse(data['created_on']),
        }

    def to_dict(self):
        return {
            'title': self.title,
            'priority': self.priority,
        }
