from utils.metadata import get_metadata
from utils.models import APIModel

import dateutil.parser


class Barrier(APIModel):
    def __init__(self, data):
        self.data = data
        metadata = get_metadata()

        self.id = data['id']
        self.code = data['code']
        self.title = data['barrier_title']
        self.product = data.get('product')
        self.location = metadata.get_location(
            data['export_country'],
            data['country_admin_areas']
        )

        if data.get('sectors'):
            self.sectors = [
                metadata.get_sector(sector_id)
                for sector_id in data['sectors']
            ]
        else:
            self.sectors = []

        if self.sectors:
            self.sector_names = [
                sector.get('name', "Unknown") for sector in self.sectors
            ]
        else:
            self.sector_names = ["All sectors"]
        status_code = str(data['status']['id'])
        self.status = metadata.get_status(status_code)
        self.problem = {
            'status': metadata.get_problem_status(self.problem_status),
            'description': data.get('problem_description')
        }
        self.priority = data['priority']
        self.reported_on = dateutil.parser.parse(data['reported_on'])
        self.modified_on = dateutil.parser.parse(data['modified_on'])
        self.added_by = data.get('reported_by')
        self.date = {
            'reported': self.reported_on,
            'status': dateutil.parser.parse(data['status']['date']),
            'created': dateutil.parser.parse(data['created_on']),
        }
        self.types = [
            metadata.get_barrier_type(barrier_type)
            for barrier_type in data['barrier_types']
        ]
        self.eu_exit_related = metadata.get_eu_exit_related_text(
            data['eu_exit_related']
        )
        self.source = {
            'id': data.get('source'),
            'name': metadata.get_source(data.get('source')),
            'description': data.get('other_source'),
        }
        if 'companies' in self.data:
            self.companies = data['companies']

        if self.export_country:
            self.country = metadata.get_country(self.export_country)
            self.admin_area_ids = self.data['country_admin_areas']

            if self.admin_area_ids:
                self.admin_areas = metadata.get_admin_areas(self.admin_area_ids)
            else:
                self.admin_areas = []

    def to_dict(self):
        return {
            'title': self.title,
            'priority': self.priority,
            'description': self.problem_description,
            'problem_status': self.problem_status,
            'eu_exit_related': self.data['eu_exit_related'],
            'product': self.product,
            'source': self.data['source'],
        }

    @property
    def is_resolved(self):
        return self.status == "RESOLVED"

    @property
    def is_partially_resolved(self):
        return self.status == "PART_RESOLVED"

    @property
    def is_open(self):
        return self.status == "OPEN"

    @property
    def is_hibernated(self):
        return self.status == "HIBERNATED"
