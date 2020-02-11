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
        assert admin_area['name'] == "Rio de Janeiro"
        assert admin_area['country']['name'] == "Brazil"

    def test_get_admin_areas_by_country(self):
        metadata = get_metadata()
        country_id = "b05f66a0-5d95-e211-a939-e4115bead28a"
        admin_areas = metadata.get_admin_areas_by_country(country_id)

        for admin_area in admin_areas:
            assert admin_area['country']['name'] == "Brazil"

    def test_get_country(self):
        metadata = get_metadata()
        country_id = "b05f66a0-5d95-e211-a939-e4115bead28a"
        country = metadata.get_country(country_id)
        assert country['id'] == country_id
        assert country['name'] == "Brazil"

    def test_get_location_text(self):
        metadata = get_metadata()
        country_id = "b05f66a0-5d95-e211-a939-e4115bead28a"
        admin_area_ids = [
            "3d4f0b93-b16e-4f61-98e8-006a2c290f95",
            "71f66703-64eb-4e00-85db-4644b9f10be8",
        ]
        assert metadata.get_location_text(country_id, []) == "Brazil"
        assert metadata.get_location_text(country_id, admin_area_ids) == (
            "Rio de Janeiro, Sao Paulo (Brazil)"
        )

    def test_get_overseas_region_list(self):
        metadata = get_metadata()
        regions = metadata.get_overseas_region_list()
        region_names = [region['name'] for region in regions]
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
        ]

    def test_get_sector(self):
        metadata = get_metadata()
        sector_id = "9838cecc-5f95-e211-a939-e4115bead28a"
        sector = metadata.get_sector(sector_id)
        assert sector['name'] == "Automotive"

    def test_get_sectors_by_ids(self):
        metadata = get_metadata()
        sector_ids = [
            "9738cecc-5f95-e211-a939-e4115bead28a",
            "9b38cecc-5f95-e211-a939-e4115bead28a",
            "b1959812-6095-e211-a939-e4115bead28a",
            "aa22c9d2-5f95-e211-a939-e4115bead28a",
        ]
        sectors = metadata.get_sectors_by_ids(sector_ids)
        sector_names = [sector['name'] for sector in sectors]
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
            assert sector['level'] == 0

    def test_get_status(self):
        metadata = get_metadata()
        assert metadata.get_status('0')['name'] == "Unfinished"
        assert metadata.get_status('1')['name'] == "Open: Pending action"
        assert metadata.get_status('2')['name'] == "Open: In progress"
        assert metadata.get_status('3')['name'] == "Resolved: In part"
        assert metadata.get_status('4')['name'] == "Resolved: In full"
        assert metadata.get_status('5')['name'] == "Dormant"
        assert metadata.get_status('6')['name'] == "Archived"
        assert metadata.get_status('7')['name'] == "Unknown"

    def test_get_status_text(self):
        metadata = get_metadata()
        assert metadata.get_status_text('2') == "Open: In progress"
        assert metadata.get_status_text('1', "UK_GOVT") == (
            "Open: Pending action (UK government)"
        )
        assert metadata.get_status_text('1', "OTHER", "Pending other") == (
            "Open: Pending action (Pending other)"
        )

    def test_get_problem_status(self):
        metadata = get_metadata()
        assert metadata.get_problem_status('1') == (
            "A procedural, short-term barrier"
        )
        assert metadata.get_problem_status('2') == (
            "A long-term strategic barrier"
        )

    def test_get_eu_exit_related_text(self):
        metadata = get_metadata()
        assert metadata.get_eu_exit_related_text('1') == "Yes"
        assert metadata.get_eu_exit_related_text('2') == "No"
        assert metadata.get_eu_exit_related_text('3') == "Don't know"

    def test_get_source(self):
        metadata = get_metadata()
        assert metadata.get_source("COMPANY") == "Company"
        assert metadata.get_source("TRADE") == "Trade association"
        assert metadata.get_source("GOVT") == "Government entity"
        assert metadata.get_source("OTHER") == "Other"

    def test_get_priority(self):
        metadata = get_metadata()
        assert metadata.get_priority("UNKNOWN")['name'] == "Unknown"
        assert metadata.get_priority("HIGH")['name'] == "High"
        assert metadata.get_priority("MEDIUM")['name'] == "Medium"
        assert metadata.get_priority("LOW")['name'] == "Low"

    def test_get_assessment_name(self):
        metadata = get_metadata()
        assert metadata.get_assessment_name("impact") == "Economic assessment"

    def test_get_barrier_type_list(self):
        metadata = get_metadata()
        barrier_types = metadata.get_barrier_type_list()
        titles = [barrier_type['title'] for barrier_type in barrier_types]

        assert "Customs procedures" in titles
        assert "Government subsidies" in titles
        assert "Rules of origin" in titles
        assert "Tariffs or import duties" in titles

    def test_get_barrier_type(self):
        metadata = get_metadata()

        barrier_type = metadata.get_barrier_type("130")

        assert barrier_type['title'] == "Price controls"
        assert barrier_type['category'] == "GOODS"

    def test_get_goods(self):
        metadata = get_metadata()

        barrier_types = metadata.get_goods()
        assert len(barrier_types) > 0
        for barrier_type in barrier_types:
            assert barrier_type['category'] == "GOODS"

    def test_get_services(self):
        metadata = get_metadata()

        barrier_types = metadata.get_services()
        assert len(barrier_types) > 0
        for barrier_type in barrier_types:
            assert barrier_type['category'] == "SERVICES"

    def test_get_impact_text(self):
        metadata = get_metadata()
        assert metadata.get_impact_text("HIGH") == "High"
        assert metadata.get_impact_text("MEDIUMHIGH") == "Medium High"
        assert metadata.get_impact_text("MEDIUMLOW") == "Medium Low"
        assert metadata.get_impact_text("LOW") == "Low"
