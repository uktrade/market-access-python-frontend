from http import HTTPStatus

from django.conf import settings
from django.urls import reverse

from barriers.models import SavedSearch
from core.tests import MarketAccessTestCase

from utils.models import ModelList

from mock import patch


class SavedSearchTestCase(MarketAccessTestCase):
    saved_search_data = {
        "id": "a18f6ddc-d4fe-48cc-afbe-8fb2e5de806f",
        "name": "Search Name",
        "filters": {"priority": ["MEDIUM"]},
        "notify_about_additions": True,
        "notify_about_updates": False,
    }

    def get_delete_url(self):
        return reverse(
            "barriers:delete_saved_search",
            kwargs={"saved_search_id": self.saved_search_data["id"]}
        )

    def get_rename_url(self):
        return reverse(
            "barriers:rename_saved_search",
            kwargs={"saved_search_id": self.saved_search_data["id"]}
        )

    @patch("utils.api.resources.APIResource.get")
    def test_rename_saved_search_initial(self, mock_get):
        mock_get.return_value = SavedSearch(self.saved_search_data)

        response = self.client.get(self.get_rename_url())
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["name"] == "Search Name"

    @patch("utils.api.resources.UsersResource.patch")
    @patch("utils.api.resources.APIResource.get")
    def test_rename_saved_search_error(self, mock_get, mock_patch):
        mock_get.return_value = SavedSearch(self.saved_search_data)

        response = self.client.post(
            self.get_rename_url(), data={"name": ""}
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "name" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.APIResource.list")
    @patch("utils.api.resources.APIResource.get")
    def test_rename_saved_search_name_conflict(self, mock_get, mock_list, mock_patch):
        mock_get.return_value = SavedSearch(self.saved_search_data)
        mock_list.return_value = [self.saved_search_data]

        response = self.client.post(
            self.get_rename_url(), data={"name": "New Name"},
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "name" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.APIResource.list")
    @patch("utils.api.resources.APIResource.get")
    def test_rename_saved_search_success(self, mock_get, mock_list, mock_patch):
        mock_get.return_value = SavedSearch(self.saved_search_data)
        mock_list.return_value = []

        response = self.client.post(
            self.get_rename_url(), data={"name": "New Name"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.saved_search_data["id"],
            name="New Name",
        )

    @patch("utils.api.resources.APIResource.delete")
    @patch("utils.api.resources.APIResource.get")
    def test_delete_saved_search(self, mock_get, mock_delete):
        mock_get.return_value = SavedSearch(self.saved_search_data)

        response = self.client.get(self.get_delete_url())
        assert response.status_code == HTTPStatus.OK

        response = self.client.post(
            self.get_delete_url(),
            data={"saved_search_id": self.saved_search_data["id"]}
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_delete.assert_called_with(self.saved_search_data["id"])

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.APIResource.list")
    def test_new_saved_search_no_name(self, mock_list, mock_patch):
        mock_list.return_value = []

        response = self.client.post(
            f"{reverse('barriers:new_saved_search')}"
            "?search=Test&priority=HIGH&status=2",
            data={"name": ""},
        )

        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "name" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.APIResource.list")
    def test_new_saved_search_name_conflict(self, mock_list, mock_patch):
        mock_list.return_value = [self.saved_search_data]

        response = self.client.post(
            f"{reverse('barriers:new_saved_search')}"
            "?search=Test&priority=HIGH&status=2",
            data={"name": "Conflicting Name"},
        )

        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "name" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.create")
    @patch("utils.api.resources.APIResource.list")
    def test_new_saved_search_success(self, mock_list, mock_create):
        mock_list.return_value = []
        mock_create.return_value = SavedSearch(self.saved_search_data)

        response = self.client.post(
            f"{reverse('barriers:new_saved_search')}"
            "?search=Test&priority=HIGH&status=2",
            data={"name": "New Name"},
        )

        assert response.status_code == HTTPStatus.FOUND

        mock_create.assert_called_with(
            name="New Name",
            filters={
                "search": "Test",
                "priority": ["HIGH"],
                "status": ["2"],
            }
        )
        assert "saved_search_created" in self.client.session

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.APIResource.list")
    @patch("utils.api.resources.APIResource.get")
    def test_update_saved_search(self, mock_get, mock_list, mock_patch):
        mock_get.return_value = SavedSearch(self.saved_search_data)

        search_id = self.saved_search_data["id"]
        response = self.client.post(
            f"{reverse('barriers:search')}"
            f"?search=Test&priority=HIGH&status=2&search_id={search_id}",
            data={"update_search": "1"}
        )

        assert response.status_code == HTTPStatus.OK

        mock_patch.assert_called_with(
            id=search_id,
            filters={
                "search": "Test",
                "priority": ["HIGH"],
                "status": ["2"],
            }
        )
        assert response.context["saved_search_updated"] is True
