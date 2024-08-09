from core.tests import MarketAccessTestCase
from utils.metadata import get_metadata


class MetadataTestCase(MarketAccessTestCase):
    """
    Test the Metadata class
    """

    def test_get_admin_area(self):
        metadata = get_metadata()
        admin_area_id = "3d4f0b93-b16e-4f61-98e8-006a2c290f95"
        admin_area = metadata.get_admin_area(admin_area_id)
        assert admin_area["name"] == "Rio de Janeiro"
        assert admin_area["country"]["name"] == "Brazil"

    def test_get_admin_areas_by_country(self):
        metadata = get_metadata()
        country_id = "b05f66a0-5d95-e211-a939-e4115bead28a"
        admin_areas = metadata.get_admin_areas_by_country(country_id)

        for admin_area in admin_areas:
            assert admin_area["country"]["name"] == "Brazil"

    def test_get_country(self):
        metadata = get_metadata()
        country_id = "b05f66a0-5d95-e211-a939-e4115bead28a"
        country = metadata.get_country(country_id)
        assert country["id"] == country_id
        assert country["name"] == "Brazil"

    def test_get_overseas_region_list(self):
        metadata = get_metadata()
        regions = metadata.get_overseas_region_list()
        region_names = [region["name"] for region in regions]
        assert region_names == [
            "Africa",
            "Asia-Pacific",
            "China",
            "Eastern Europe and Central Asia",
            "Europe",
            "Latin America",
            "Middle East",
            "North America",
            "South Asia",
            "Wider Europe",
        ]

    def test_get_sector(self):
        metadata = get_metadata()
        sector_id = "9838cecc-5f95-e211-a939-e4115bead28a"
        sector = metadata.get_sector(sector_id)
        assert sector["name"] == "Automotive"

    def test_get_sectors_by_ids(self):
        metadata = get_metadata()
        sector_ids = [
            "9738cecc-5f95-e211-a939-e4115bead28a",
            "9b38cecc-5f95-e211-a939-e4115bead28a",
            "b1959812-6095-e211-a939-e4115bead28a",
            "aa22c9d2-5f95-e211-a939-e4115bead28a",
        ]
        sectors = metadata.get_sectors_by_ids(sector_ids)
        sector_names = [sector["name"] for sector in sectors]
        assert sector_names == [
            "Airports",
            "Chemicals",
            "Energy",
            "Railways",
        ]

    def test_get_sector_list(self):
        metadata = get_metadata()
        sectors = metadata.get_sector_list(level=0)
        assert len(sectors) > 0
        for sector in sectors:
            assert sector["level"] == 0

    def test_get_status(self):
        metadata = get_metadata()
        assert metadata.get_status("0")["name"] == "Unfinished"
        assert metadata.get_status("2")["name"] == "Open"
        assert metadata.get_status("3")["name"] == "Resolved: In part"
        assert metadata.get_status("4")["name"] == "Resolved: In full"
        assert metadata.get_status("5")["name"] == "Dormant"
        assert metadata.get_status("6")["name"] == "Archived"
        assert metadata.get_status("7")["name"] == "Unknown"

    def test_get_status_text(self):
        metadata = get_metadata()
        assert metadata.get_status_text("2") == "Open"

    def test_get_term(self):
        metadata = get_metadata()
        assert metadata.get_term("1") == "A procedural, short-term barrier"
        assert metadata.get_term("2") == "A long-term strategic barrier"

    def test_get_source(self):
        metadata = get_metadata()
        assert metadata.get_source("COMPANY") == "Company"
        assert metadata.get_source("TRADE") == "Trade association"
        assert metadata.get_source("GOVT") == "Government entity"
        assert metadata.get_source("OTHER") == "Other"

    def test_get_priority(self):
        metadata = get_metadata()
        assert metadata.get_priority("UNKNOWN")["name"] == "Unknown"
        assert metadata.get_priority("HIGH")["name"] == "High"
        assert metadata.get_priority("MEDIUM")["name"] == "Medium"
        assert metadata.get_priority("LOW")["name"] == "Low"

    def test_get_category_list(self):
        metadata = get_metadata()
        categories = metadata.get_category_list()
        titles = [category["title"] for category in categories]

        assert "Customs procedures" in titles
        assert "Government subsidies" in titles
        assert "Rules of origin" in titles
        assert "Tariffs or import duties" in titles

    def test_get_category(self):
        metadata = get_metadata()

        category = metadata.get_category("130")

        assert category["title"] == "Price controls"
        assert category["category"] == "GOODS"

    def test_get_policy_team_list(self):
        metadata = get_metadata()
        policy_teams = metadata.get_policy_team_list()
        titles = [policy_team["title"] for policy_team in policy_teams]

        assert "Competition" in titles
        assert "Customs" in titles
        assert "Digital and Telecoms" in titles
        assert "Environment and climate" in titles

    def test_get_policy_team(self):
        metadata = get_metadata()

        policy_team = metadata.get_policy_team("1")

        assert policy_team["title"] == "Competition"
        assert "Competition policy is about making sure UK firms" in policy_team["description"]

    def test_get_goods(self):
        metadata = get_metadata()

        barrier_types = metadata.get_goods()
        assert len(barrier_types) > 0
        for barrier_type in barrier_types:
            assert barrier_type["category"] == "GOODS"

    def test_get_services(self):
        metadata = get_metadata()

        barrier_types = metadata.get_services()
        assert len(barrier_types) > 0
        for barrier_type in barrier_types:
            assert barrier_type["category"] == "SERVICES"

    def test_get_tag_that_does_not_exist(self):
        metadata = get_metadata()

        tag_id = 999999
        tag = metadata.get_barrier_tag(tag_id=tag_id)
        assert tag == {
            "id": tag_id,
            "title": "[unknown tag]",
            "description": "No such tag exists",
            "show_at_reporting": False,
            "order": 9999,
        }
