from http import HTTPStatus

from django.conf import settings
from django.urls import reverse

from barriers.models import Barrier, SavedSearch
from core.tests import MarketAccessTestCase
from utils.metadata import get_metadata
from utils.models import ModelList

from mock import patch


@patch("utils.pagination.PaginationMixin.pagination_limit", 10)
class SearchTestCase(MarketAccessTestCase):
    saved_search_data = {
        "id": "a18f6ddc-d4fe-48cc-afbe-8fb2e5de806f",
        "name": "Search Name",
        "filters": {"priority": ["MEDIUM"]},
        "notify_about_additions": True,
        "notify_about_updates": False,
    }

    @patch("utils.api.resources.APIResource.list")
    def test_empty_search(self, mock_list):
        response = self.client.get(reverse("barriers:search"))
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported_on",
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
        country_choices = form.fields["country"].choices
        assert len(country_choices) == len(country_list) + 1

        sector_list = metadata.get_sector_list(level=0)
        sector_choices = form.fields["sector"].choices
        assert len(sector_choices) == len(sector_list) + 1

        category_list = set([category["id"] for category in metadata.data["categories"]])
        category_choices = form.fields["category"].choices
        assert len(category_choices) == len(category_list) + 1

        region_list = set(
            [region["id"] for region in metadata.get_overseas_region_list()]
        )
        region_choices = form.fields["region"].choices
        assert len(region_choices) == len(region_list) + 1

        priority_list = metadata.data["barrier_priorities"]
        priority_choices = form.fields["priority"].choices
        assert len(priority_choices) == len(priority_list)

        status_choices = form.fields["status"].choices
        assert len(status_choices) == 6

    @patch("utils.api.resources.APIResource.list")
    def test_search_filters(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"),
            data={
                "search": "Test search",
                "country": [
                    "9f5f66a0-5d95-e211-a939-e4115bead28a",
                    "83756b9a-5d95-e211-a939-e4115bead28a",
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
                "priority": ["HIGH", "MEDIUM"],
                "status": ["1", "2", "7"],
                "user": "1",
            },
        )
        assert response.status_code == HTTPStatus.OK

        form = response.context["form"]
        assert form.cleaned_data["search"] == "Test search"
        assert form.cleaned_data["country"] == [
            "9f5f66a0-5d95-e211-a939-e4115bead28a",
            "83756b9a-5d95-e211-a939-e4115bead28a",
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
        assert form.cleaned_data["priority"] == ["HIGH", "MEDIUM"]
        assert form.cleaned_data["status"] == ["1", "2", "7"]
        assert form.cleaned_data["user"] == "1"

        mock_list.assert_called_with(
            ordering="-reported_on",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            search="Test search",
            location=(
                "9f5f66a0-5d95-e211-a939-e4115bead28a,"
                "83756b9a-5d95-e211-a939-e4115bead28a,"
                "3e6809d6-89f6-4590-8458-1d0dab73ad1a,"
                "5616ccf5-ab4a-4c2c-9624-13c69be3c46b"
            ),
            sector=(
                "9538cecc-5f95-e211-a939-e4115bead28a,"
                "aa22c9d2-5f95-e211-a939-e4115bead28a"
            ),
            category="130,141",
            priority="HIGH,MEDIUM",
            status="1,2,7",
            user="1",
            archived="0",
        )

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.list")
    def test_my_barriers_filter(self, mock_list, mock_get):
        mock_get.return_value = SavedSearch(
            data={
                "name": "My barriers",
                "filters": {"user": "1"},
                "notify_about_additions": True,
                "notify_about_updates": False,
            }
        )
        response = self.client.get(
            reverse("barriers:search"), data={"user": "1"},
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported_on",
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
            reverse("barriers:search"), data={"team": "1"},
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported_on",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            team="1",
            archived="0",
        )
        mock_get.assert_called_with("team-barriers")
        assert response.context["search_title"] == "Team barriers"

        response = self.client.get(
            reverse("barriers:search"), data={"user": "1", "team": "1"},
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported_on",
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
            data={"priority": "MEDIUM", "search_id": saved_search.id},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.context["saved_search"].id == saved_search.id
        assert response.context["have_filters_changed"] is False
        assert response.context["search_title"] is saved_search.name

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.list")
    def test_saved_search_with_changed_filters(self, mock_list, mock_get):
        saved_search = SavedSearch(self.saved_search_data)
        mock_get.return_value = saved_search

        response = self.client.get(
            reverse("barriers:search"),
            data={"priority": "MEDIUM", "search": "yo", "search_id": saved_search.id},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.context["saved_search"].id == saved_search.id
        assert response.context["have_filters_changed"] is True
        assert response.context["search_title"] is saved_search.name

    @patch("utils.api.resources.APIResource.list")
    def test_archived_filter(self, mock_list):
        response = self.client.get(
            reverse("barriers:search"), data={"only_archived": "1"},
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported_on",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            archived="1",
        )

    @patch("utils.api.resources.APIResource.list")
    def test_pagination(self, mock_list):
        mock_list.return_value = ModelList(
            model=Barrier, data=[self.barrier] * 10, total_count=123,
        )

        response = self.client.get(
            reverse("barriers:search"),
            data={"status": ["1", "2", "3", "4", "5"], "page": "6"},
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported_on",
            archived="0",
            status="1,2,3,4,5",
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
            "status=1&status=2&status=3&status=4&status=5&page=1"
        )
        page_labels = [page["label"] for page in pagination["pages"]]
        assert page_labels == [1, "...", 5, 6, 7, 8, "...", 13]

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
                ]
            },
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported_on",
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
