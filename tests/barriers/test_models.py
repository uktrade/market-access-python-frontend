import datetime
from core.tests import MarketAccessTestCase

from barriers.models import Barrier, Company, SavedSearch


class BarrierModelTestCase(MarketAccessTestCase):
    def test_fields(self):
        barrier = Barrier(self.barrier)
        assert barrier.country["name"] == "Brazil"
        assert barrier.admin_areas[0]["name"] == "Rio de Janeiro"

        assert barrier.created_on.date() == datetime.date(2019, 10, 28)
        assert barrier.reported_on.date() == datetime.date(2019, 10, 28)
        assert barrier.modified_on.date() == datetime.date(2020, 1, 21)

        assert barrier.location == "Rio de Janeiro, Sao Paulo (Brazil)"
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


class SavedSearchModelTestCase(MarketAccessTestCase):
    old_user_saved_search = {
        "name": "Old user saved search",
        "filters": {"search": ["Test"], "createdBy": ["1"]},
    }
    old_team_saved_search = {
        "name": "Old team saved search",
        "filters": {"search": ["Test"], "createdBy": ["2"]},
    }
    complex_saved_search = {
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
            "user": 1,
        },
    }

    def test_field_conversion_user(self):
        saved_search = SavedSearch(self.old_user_saved_search)
        assert saved_search.filters == {"search": "Test", "user": 1}

    def test_field_conversion_team(self):
        saved_search = SavedSearch(self.old_team_saved_search)
        assert saved_search.filters == {"search": "Test", "team": 1}

    def test_readable_filters(self):
        saved_search = SavedSearch(self.complex_saved_search)
        assert saved_search.readable_filters["search"] == {
            "label": "Search",
            "readable_value": "Test",
            "value": "Test",
        }
        assert saved_search.readable_filters["country"] == {
            "label": "Barrier location",
            "readable_value": "Australia",
            "value": ["9f5f66a0-5d95-e211-a939-e4115bead28a"],
        }
        assert saved_search.readable_filters["sector"] == {
            "label": "Sector",
            "readable_value": "Aerospace, Food and Drink",
            "value": [
                "9538cecc-5f95-e211-a939-e4115bead28a",
                "a538cecc-5f95-e211-a939-e4115bead28a",
            ],
        }
        assert saved_search.readable_filters["type"] == {
            "label": "Barrier type",
            "readable_value": "Government subsidies",
            "value": ["127"],
        }
        assert saved_search.readable_filters["region"] == {
            "label": "Overseas region",
            "readable_value": "Europe",
            "value": ["3e6809d6-89f6-4590-8458-1d0dab73ad1a"],
        }
        assert saved_search.readable_filters["priority"] == {
            "label": "Barrier priority",
            "readable_value": (
                "<span class='priority-marker priority-marker--high'>"
                "</span>High, "
                "<span class='priority-marker priority-marker--medium'>"
                "</span>Medium"
            ),
            "value": ["HIGH", "MEDIUM"],
        }
        assert saved_search.readable_filters["status"] == {
            "label": "Barrier status",
            "readable_value": "Open: In progress, Resolved: In part",
            "value": ["2", "3"],
        }
        assert saved_search.readable_filters["show"] == {
            "label": "Show",
            "readable_value": "My barriers",
            "value": ["1"],
        }

    def test_get_api_params(self):
        saved_search = SavedSearch(self.complex_saved_search)
        assert saved_search.get_api_params() == {
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
