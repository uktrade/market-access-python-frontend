import datetime
from core.tests import MarketAccessTestCase

from barriers.models import Barrier, Company


class BarrierModelTestCase(MarketAccessTestCase):

    def test_fields(self):
        barrier = Barrier(self.barrier)
        assert barrier.country['name'] == "Brazil"
        assert barrier.admin_areas[0]['name'] == "Rio de Janeiro"

        assert barrier.created_on.date() == datetime.date(2019, 10, 28)
        assert barrier.reported_on.date() == datetime.date(2019, 10, 28)
        assert barrier.modified_on.date() == datetime.date(2020, 1, 21)

        assert barrier.location == "Rio de Janeiro, Sao Paulo (Brazil)"
        assert barrier.eu_exit_related_text == "No"
        assert barrier.problem_status_text == "A long-term strategic barrier"
        assert barrier.sectors[0]['name'] == "Automotive"
        assert barrier.sector_names == ["Automotive"]
        assert barrier.source_name == "Government entity"
        assert barrier.status['name'] == "Resolved: In full"
        assert barrier.title == "Import quota for sports cars"
        assert barrier.types[0]['title'] == "Import quotas"
        assert barrier.types[1]['title'] == "Tariffs or import duties"

        assert barrier.is_resolved is True
        assert barrier.is_partially_resolved is False
        assert barrier.is_open is False
        assert barrier.is_hibernated is False


class CompanyModelTestCase(MarketAccessTestCase):

    def test_fields(self):
        company = Company({
            'id': "0692683e-5197-4853-a0fe-e43e35b8e7c5",
            'name': "Test Company",
            'created_on': '2020-01-01',
            'address': {
                'line_1': "123 Test Street",
                'town': "London",
                'country': {
                    'name': 'UK'
                }
            },
        })
        assert company.get_address_display() == "123 Test Street, London, UK"
        assert company.created_on.date() == datetime.date(2020, 1, 1)
