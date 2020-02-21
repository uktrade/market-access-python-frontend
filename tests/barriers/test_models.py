import datetime
from core.tests import MarketAccessTestCase

from barriers.models import Barrier, Company, Watchlist


class BarrierModelTestCase(MarketAccessTestCase):
    def test_fields(self):
        barrier = Barrier(self.barrier)
        assert barrier.country["name"] == "Brazil"
        assert barrier.admin_areas[0]["name"] == "Rio de Janeiro"

        assert barrier.created_on.date() == datetime.date(2019, 10, 28)
        assert barrier.reported_on.date() == datetime.date(2019, 10, 28)
        assert barrier.modified_on.date() == datetime.date(2020, 1, 21)

        assert barrier.location == "Rio de Janeiro, Sao Paulo (Brazil)"
        assert barrier.eu_exit_related_text == "No"
        assert barrier.problem_status_text == "A long-term strategic barrier"
        assert barrier.sectors[0]["name"] == "Automotive"
        assert barrier.sector_names == ["Automotive"]
        assert barrier.source_name == "Government entity"
        assert barrier.status["name"] == "Resolved: In full"
        assert barrier.title == "Import quota for sports cars"
        assert barrier.types[0]["title"] == "Import quotas"
        assert barrier.types[1]["title"] == "Tariffs or import duties"

        assert barrier.is_resolved is True
        assert barrier.is_partially_resolved is False
        assert barrier.is_open is False
        assert barrier.is_hibernated is False


class CompanyModelTestCase(MarketAccessTestCase):
    def test_fields(self):
        company = Company(
            {
                "id": "0692683e-5197-4853-a0fe-e43e35b8e7c5",
                "name": "Test Company",
                "created_on": "2020-01-01",
                "address": {
                    "line_1": "123 Test Street",
                    "town": "London",
                    "country": {"name": "UK"},
                },
            }
        )
        assert company.get_address_display() == "123 Test Street, London, UK"
        assert company.created_on.date() == datetime.date(2020, 1, 1)


class WatchlistModelTestCase(MarketAccessTestCase):
    old_watchlist = {
        "name": "Old watchlist",
        "filters": {"search": ["Test"], "createdBy": ["1"]},
    }
    complex_watchlist = {
        "name": "Complex",
        "filters": {
            "search": "Test",
            "country": ["9f5f66a0-5d95-e211-a939-e4115bead28a"],
            "sector": [
                "9538cecc-5f95-e211-a939-e4115bead28a",
                "a538cecc-5f95-e211-a939-e4115bead28a",
            ],
            "type": ["127"],
            "region": ["3e6809d6-89f6-4590-8458-1d0dab73ad1a"],
            "priority": ["HIGH", "MEDIUM"],
            "status": ["2", "3"],
            "created_by": ["1"],
        },
    }

    def test_field_conversion(self):
        watchlist = Watchlist(**self.old_watchlist)
        assert watchlist.filters == {"search": "Test", "created_by": ["1"]}

    def test_readable_filters(self):
        watchlist = Watchlist(**self.complex_watchlist)
        assert watchlist.readable_filters["search"] == {
            "label": "Search",
            "readable_value": "Test",
            "value": "Test",
        }
        assert watchlist.readable_filters["country"] == {
            "label": "Barrier location",
            "readable_value": "Australia",
            "value": ["9f5f66a0-5d95-e211-a939-e4115bead28a"],
        }
        assert watchlist.readable_filters["sector"] == {
            "label": "Sector",
            "readable_value": "Aerospace, Food and Drink",
            "value": [
                "9538cecc-5f95-e211-a939-e4115bead28a",
                "a538cecc-5f95-e211-a939-e4115bead28a",
            ],
        }
        assert watchlist.readable_filters["type"] == {
            "label": "Barrier type",
            "readable_value": "Government subsidies",
            "value": ["127"],
        }
        assert watchlist.readable_filters["region"] == {
            "label": "Overseas region",
            "readable_value": "Europe",
            "value": ["3e6809d6-89f6-4590-8458-1d0dab73ad1a"],
        }
        assert watchlist.readable_filters["priority"] == {
            "label": "Barrier priority",
            "readable_value": (
                "<span class='priority-marker priority-marker--high'>"
                "</span>High, "
                "<span class='priority-marker priority-marker--medium'>"
                "</span>Medium"
            ),
            "value": ["HIGH", "MEDIUM"],
        }
        assert watchlist.readable_filters["status"] == {
            "label": "Barrier status",
            "readable_value": "Open: In progress, Resolved: In part",
            "value": ["2", "3"],
        }
        assert watchlist.readable_filters["created_by"] == {
            "label": "Show only",
            "readable_value": "My barriers",
            "value": ["1"],
        }

    def test_get_api_params(self):
        watchlist = Watchlist(**self.complex_watchlist)
        assert watchlist.get_api_params() == {
            "text": "Test",
            "location": (
                "9f5f66a0-5d95-e211-a939-e4115bead28a,"
                "3e6809d6-89f6-4590-8458-1d0dab73ad1a"
            ),
            "sector": (
                "9538cecc-5f95-e211-a939-e4115bead28a,"
                "a538cecc-5f95-e211-a939-e4115bead28a"
            ),
            "barrier_type": "127",
            "priority": "HIGH,MEDIUM",
            "status": "2,3",
            "user": 1,
        }
