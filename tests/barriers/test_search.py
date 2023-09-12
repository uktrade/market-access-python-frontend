import logging
from http import HTTPStatus

from django.conf import settings
from django.urls import reverse
from mock import patch

from barriers.models import Barrier, SavedSearch
from core.tests import MarketAccessTestCase
from utils.metadata import get_metadata
from utils.models import ModelList

logger = logging.getLogger(__name__)


@patch("utils.pagination.PaginationMixin.pagination_limit", 10)
class SearchTestCase(MarketAccessTestCase):
    saved_search_data = {
        "id": "a18f6ddc-d4fe-48cc-afbe-8fb2e5de806f",
        "name": "Search Name",
        "filters": {"status": "OPEN_IN_PROGRESS"},
        "notify_about_additions": True,
        "notify_about_updates": False,
    }

    @patch("utils.api.resources.APIResource.list")
    def test_empty_search(self, mock_list):
        response = self.client.get(reverse("barriers:search"))
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            archived="0",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
        )

    @patch("utils.api.resources.APIResource.list")
    def test_search_form_choices(self, mock_list):
        response = self.client.get(reverse("barriers:search"))
        assert response.status_code == HTTPStatus.OK

        form = response.context["form"]

        metadata = get_metadata()
        country_list = metadata.get_country_list()
        trading_bloc_list = metadata.get_trading_bloc_list()
        country_choices = form.fields["country"].choices
        assert len(country_choices) == len(country_list) + len(trading_bloc_list)

        sector_list = metadata.get_sector_list(level=0)
        sector_choices = form.fields["sector"].choices
        assert len(sector_choices) == len(sector_list)

        category_list = set(
            [category["id"] for category in metadata.data["categories"]]
        )
        category_choices = form.fields["category"].choices
        assert len(category_choices) == len(category_list)

        region_list = set(
            [region["id"] for region in metadata.get_overseas_region_list()]
        )
        region_choices = form.fields["region"].choices
        assert len(region_choices) == len(region_list)

        status_choices = form.fields["status"].choices
        assert len(status_choices) == 4

    @patch("utils.api.resources.APIResource.list")
    def test_search_filters(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"),
            data={
                "search": "Test search",
                "country": [
                    "9f5f66a0-5d95-e211-a939-e4115bead28a",
                    "83756b9a-5d95-e211-a939-e4115bead28a",
                    "TB00016",
                ],
                "sector": [
                    "9538cecc-5f95-e211-a939-e4115bead28a",
                    "aa22c9d2-5f95-e211-a939-e4115bead28a",
                ],
                "category": ["130", "141"],
                "region": [
                    "3e6809d6-89f6-4590-8458-1d0dab73ad1a",
                    "5616ccf5-ab4a-4c2c-9624-13c69be3c46b",
                ],
                "status": ["2"],
                "user": "1",
                "ordering": "-reported",
            },
        )
        assert response.status_code == HTTPStatus.OK

        form = response.context["form"]
        assert form.cleaned_data["search"] == "Test search"
        assert form.cleaned_data["country"] == [
            "9f5f66a0-5d95-e211-a939-e4115bead28a",
            "83756b9a-5d95-e211-a939-e4115bead28a",
            "TB00016",
        ]
        assert form.cleaned_data["sector"] == [
            "9538cecc-5f95-e211-a939-e4115bead28a",
            "aa22c9d2-5f95-e211-a939-e4115bead28a",
        ]
        assert form.cleaned_data["category"] == ["130", "141"]
        assert form.cleaned_data["region"] == [
            "3e6809d6-89f6-4590-8458-1d0dab73ad1a",
            "5616ccf5-ab4a-4c2c-9624-13c69be3c46b",
        ]
        assert form.cleaned_data["status"] == ["2"]
        assert form.cleaned_data["user"] == "1"

        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            search="Test search",
            location=(
                "9f5f66a0-5d95-e211-a939-e4115bead28a,"
                "83756b9a-5d95-e211-a939-e4115bead28a,"
                "TB00016,"
                "3e6809d6-89f6-4590-8458-1d0dab73ad1a,"
                "5616ccf5-ab4a-4c2c-9624-13c69be3c46b"
            ),
            sector=(
                "9538cecc-5f95-e211-a939-e4115bead28a,"
                "aa22c9d2-5f95-e211-a939-e4115bead28a"
            ),
            category="130,141",
            status="2",
            user="1",
            archived="0",
        )

    @patch("utils.api.resources.APIResource.list")
    def test_include_eu_wide_search_filter(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"),
            data={
                "extra_location": ["TB00016"],
                "country": ["82756b9a-5d95-e211-a939-e4115bead28a"],
                "ordering": "-reported",
            },
        )
        assert response.status_code == HTTPStatus.OK

        form = response.context["form"]
        assert form.cleaned_data["country"] == [
            "82756b9a-5d95-e211-a939-e4115bead28a",
        ]
        assert form.cleaned_data["extra_location"] == ["TB00016"]

        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            location="82756b9a-5d95-e211-a939-e4115bead28a,TB00016",
            archived="0",
        )

    @patch("utils.api.resources.APIResource.list")
    def test_admin_areas_search_filter(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"),
            data={
                "country": [
                    "63af72a6-5d95-e211-a939-e4115bead28a",
                    "5961b8be-5d95-e211-a939-e4115bead28a",
                ],
                "admin_areas": (
                    '{"63af72a6-5d95-e211-a939-e4115bead28a":["56f5f425-e3e3-4c9a-b886-ecb671b81503"],'
                    '"5961b8be-5d95-e211-a939-e4115bead28a":["2384702f-01e9-4792-857b-026b2623f2fa"]}'
                ),
                "ordering": "-reported",
            },
        )
        assert response.status_code == HTTPStatus.OK

        form = response.context["form"]
        assert form.cleaned_data["country"] == [
            "63af72a6-5d95-e211-a939-e4115bead28a",
            "5961b8be-5d95-e211-a939-e4115bead28a",
        ]
        assert form.cleaned_data["admin_areas"] == {
            "63af72a6-5d95-e211-a939-e4115bead28a": [
                "56f5f425-e3e3-4c9a-b886-ecb671b81503"
            ],
            "5961b8be-5d95-e211-a939-e4115bead28a": [
                "2384702f-01e9-4792-857b-026b2623f2fa"
            ],
        }

        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            location="63af72a6-5d95-e211-a939-e4115bead28a,5961b8be-5d95-e211-a939-e4115bead28a",
            admin_areas="56f5f425-e3e3-4c9a-b886-ecb671b81503,2384702f-01e9-4792-857b-026b2623f2fa",
            archived="0",
        )

    @patch("utils.api.resources.APIResource.list")
    def test_country_specific_trading_bloc_search_filter(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"),
            data={
                "country": ["TB00016"],
                "country_trading_bloc": ["TB00016"],
                "ordering": "-reported",
            },
        )
        assert response.status_code == HTTPStatus.OK

        form = response.context["form"]
        assert form.cleaned_data["country"] == ["TB00016"]
        assert form.cleaned_data["country_trading_bloc"] == ["TB00016"]

        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            location="TB00016",
            country_trading_bloc="TB00016",
            archived="0",
        )

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.list")
    def test_my_barriers_filter(self, mock_list, mock_get):
        mock_get.return_value = SavedSearch(
            data={
                "name": "My barriers",
                "filters": {
                    "user": "1",
                },
                "notify_about_additions": True,
                "notify_about_updates": False,
            }
        )
        response = self.client.get(
            reverse("barriers:search"),
            data={"user": "1", "ordering": "-reported"},
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            user="1",
            archived="0",
        )
        mock_get.assert_called_with("my-barriers")
        assert response.context["search_title"] == "My barriers"

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.list")
    def test_my_team_barriers_filter(self, mock_list, mock_get):
        mock_get.return_value = SavedSearch(
            data={
                "name": "Team barriers",
                "filters": {"team": "1"},
                "notify_about_additions": True,
                "notify_about_updates": False,
            }
        )
        response = self.client.get(
            reverse("barriers:search"),
            data={
                "team": "1",
                "ordering": "-reported",
            },
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            team="1",
            archived="0",
        )
        mock_get.assert_called_with("team-barriers")
        assert response.context["search_title"] == "Team barriers"

        response = self.client.get(
            reverse("barriers:search"),
            data={
                "user": "1",
                "team": "1",
                "ordering": "-reported",
            },
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            team="1",
            user="1",
            archived="0",
        )

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.list")
    def test_saved_search(self, mock_list, mock_get):
        saved_search = SavedSearch(self.saved_search_data)
        mock_get.return_value = saved_search

        response = self.client.get(
            reverse("barriers:search"),
            data={"status": "2", "search_id": saved_search.id},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.context["saved_search"].id == saved_search.id
        assert response.context["have_filters_changed"] is True
        assert response.context["search_title"] is saved_search.name

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.list")
    def test_saved_search_with_changed_filters(self, mock_list, mock_get):
        saved_search = SavedSearch(self.saved_search_data)
        mock_get.return_value = saved_search

        response = self.client.get(
            reverse("barriers:search"),
            data={"status": "2", "search": "yo", "search_id": saved_search.id},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.context["saved_search"].id == saved_search.id
        assert response.context["have_filters_changed"] is True
        assert response.context["search_title"] is saved_search.name

    @patch("utils.api.resources.APIResource.list")
    def test_archived_filter(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"),
            data={"only_archived": "1", "ordering": "-reported"},
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            archived="1",
        )

    @patch("utils.api.resources.APIResource.list")
    def test_pagination(self, mock_list):
        mock_list.return_value = ModelList(
            model=Barrier,
            data=[self.barrier] * 10,
            total_count=123,
        )

        response = self.client.get(
            reverse("barriers:search"),
            data={
                "status": ["2", "3", "4", "5"],
                "page": "6",
                "ordering": "-reported",
            },
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported",
            archived="0",
            status="2,3,4,5",
            limit=10,
            offset=50,
        )
        barriers = response.context["barriers"]
        assert len(barriers) == 10
        assert barriers.total_count == 123

        pagination = response.context["pagination"]
        assert pagination["total_pages"] == 13
        assert pagination["pages"][0]["label"] == 1
        assert pagination["pages"][0]["url"] == (
            "status=2&status=3&status=4&status=5&ordering=-reported&page=1"
        )
        page_labels = [page["label"] for page in pagination["pages"]]
        assert page_labels == [1, "...", 5, 6, 7, 8, "...", 13]

    @patch("utils.api.resources.APIResource.list")
    def test_pagination_x_to_y_of_z_full_page(self, mock_list):
        mock_list.return_value = ModelList(
            model=Barrier,
            data=[self.barrier] * 10,
            total_count=30,
        )

        response = self.client.get(
            reverse("barriers:search"),
            data={"status": ["2", "3"], "page": "3", "ordering": "-reported"},
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported",
            archived="0",
            status="2,3",
            limit=10,
            offset=20,
        )

        pagination = response.context["pagination"]
        assert pagination["total_pages"] == 3
        assert pagination["current_page"] == 3
        assert pagination["total_items"] == 30
        assert pagination["start_position"] == 21
        assert pagination["end_position"] == 30

    @patch("utils.api.resources.APIResource.list")
    def test_pagination_x_to_y_of_z_partial_page(self, mock_list):
        mock_list.return_value = ModelList(
            model=Barrier,
            data=[self.barrier] * 10,
            total_count=23,
        )

        response = self.client.get(
            reverse("barriers:search"),
            data={"status": ["2", "3"], "page": "3", "ordering": "-reported"},
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported",
            archived="0",
            status="2,3",
            limit=10,
            offset=20,
        )

        pagination = response.context["pagination"]
        assert pagination["total_pages"] == 3
        assert pagination["current_page"] == 3
        assert pagination["total_items"] == 23
        assert pagination["start_position"] == 21
        assert pagination["end_position"] == 23

    @patch("utils.api.resources.APIResource.list")
    def test_pagination_x_to_y_of_z_page_before_partial_page(self, mock_list):
        mock_list.return_value = ModelList(
            model=Barrier,
            data=[self.barrier] * 10,
            total_count=23,
        )

        response = self.client.get(
            reverse("barriers:search"),
            data={"status": ["2", "3"], "page": "2", "ordering": "-reported"},
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported",
            archived="0",
            status="2,3",
            limit=10,
            offset=10,
        )

        pagination = response.context["pagination"]
        assert pagination["total_pages"] == 3
        assert pagination["current_page"] == 2
        assert pagination["total_items"] == 23
        assert pagination["start_position"] == 11
        assert pagination["end_position"] == 20

    @patch("utils.api.resources.APIResource.list")
    def test_wto_filters(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"),
            data={
                "wto": [
                    "wto_has_been_notified",
                    "wto_should_be_notified",
                    "has_raised_date",
                    "has_committee_raised_in",
                    "has_case_number",
                    "has_no_information",
                ],
                "ordering": "-reported",
            },
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            archived="0",
            wto=(
                "wto_has_been_notified,"
                "wto_should_be_notified,"
                "has_raised_date,"
                "has_committee_raised_in,"
                "has_case_number,"
                "has_no_information"
            ),
        )

    @patch("utils.api.resources.APIResource.list")
    def test_empty_resolution_date_filters(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"),
            data={
                "status": ["4"],
                "resolved_date_from_month": "",
                "resolved_date_from_year": "",
                "resolved_date_to_month": "",
                "resolved_date_to_year": "",
                "ordering": "-reported",
            },
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            archived="0",
            status="4",
        )

    @patch("utils.api.resources.APIResource.list")
    def test_resolution_date_filters_resolved_in_full(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"),
            data={
                "status": ["4"],
                "resolved_date_from_month_resolved_in_full": "01",
                "resolved_date_from_year_resolved_in_full": "2021",
                "resolved_date_to_month_resolved_in_full": "01",
                "resolved_date_to_year_resolved_in_full": "2022",
                "ordering": "-reported",
            },
        )

        assert response.status_code == HTTPStatus.OK

        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            archived="0",
            status="4",
            status_date_resolved_in_full="2021-01-01,2022-01-31",
        )

    @patch("utils.api.resources.APIResource.list")
    def test_resolution_date_filters_resolved_in_part(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"),
            data={
                "status": ["3"],
                "resolved_date_from_month_resolved_in_part": "01",
                "resolved_date_from_year_resolved_in_part": "2021",
                "resolved_date_to_month_resolved_in_part": "01",
                "resolved_date_to_year_resolved_in_part": "2022",
                "ordering": "-reported",
            },
        )

        assert response.status_code == HTTPStatus.OK

        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            archived="0",
            status="3",
            status_date_resolved_in_part="2021-01-01,2022-01-31",
        )

    @patch("utils.api.resources.APIResource.list")
    def test_resolution_date_filters_open_in_progress(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"),
            data={
                "status": ["2"],
                "resolved_date_from_month_open_in_progress": "01",
                "resolved_date_from_year_open_in_progress": "2021",
                "resolved_date_to_month_open_in_progress": "01",
                "resolved_date_to_year_open_in_progress": "2022",
                "ordering": "-reported",
            },
        )

        assert response.status_code == HTTPStatus.OK

        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            archived="0",
            status="2",
            status_date_open_in_progress="2021-01-01,2022-01-31",
        )

    @patch("utils.api.resources.APIResource.list")
    def test_delivery_confidence_filter(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"),
            data={"delivery_confidence": "ON_TRACK", "ordering": "-reported"},
        )

        assert response.status_code == HTTPStatus.OK

        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            archived="0",
            delivery_confidence="ON_TRACK",
        )

    @patch("utils.api.resources.APIResource.list")
    def test_start_date_range_filter(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"),
            data={
                "start_date_from_month": "01",
                "start_date_from_year": "2021",
                "start_date_to_month": "01",
                "start_date_to_year": "2022",
                "ordering": "-reported",
            },
        )

        assert response.status_code == HTTPStatus.OK

        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            archived="0",
            start_date="2021-01-01,2022-01-31",
        )

    @patch("utils.api.resources.APIResource.list")
    def test_export_types_filter(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"),
            data={"export_types": ["goods", "services"], "ordering": "-reported"},
        )

        assert response.status_code == HTTPStatus.OK

        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            archived="0",
            export_types="goods,services",
        )

    @patch("utils.api.resources.APIResource.list")
    def test_only_main_sector(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"),
            data={"only_main_sector": True, "ordering": "-reported"},
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            archived="0",
            only_main_sector="yes",
        )
