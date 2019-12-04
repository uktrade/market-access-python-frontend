import dateutil.parser

from django.db import models


class Barrier:
    def __init__(self, data):
        self.id = data['id']
        self.code = data['code']
        self.title = data['barrier_title']
        # 'isOpen': ( barrierStatusCode == OPEN ),
        # 'isResolved': ( barrierStatusCode == RESOLVED ),
        # 'isHibernated': ( barrierStatusCode == HIBERNATED ),
        #'location': strings.location( barrier.export_country, barrier.country_admin_areas ),
        self.sectors = []
        #'sectorsList': sectors.map( ( sector ) => sector.name ),
        self.status = ""
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
