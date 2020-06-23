from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase
from users.models import PermissionGroup, User

from mock import patch


class ManageUsersTestCase(MarketAccessTestCase):
    @patch("utils.sso.SSOClient.search_users")
    def test_no_results(self, mock_search_users):
        mock_search_users.return_value = []
        response = self.client.post(reverse("users:add_user"))
        assert response.status_code == HTTPStatus.OK
        assert mock_search_users.called is True
        assert response.context["form"].is_valid() is True
        assert response.context["results"] == []

    @patch("utils.sso.SSOClient.search_users")
    def test_with_results(self, mock_search_users):
        results = [
            {
                "user_id": "3fbe6479-b9bd-4658-81d7-f07c2a73d33d",
                "first_name": "Douglas",
                "last_name": "Miller",
                "email": "Flo_Schultz67@hotmail.com",
            }
        ]
        mock_search_users.return_value = results
        response = self.client.post(
            reverse("users:add_user"),
            data={"query": "Test search"},
        )
        assert response.status_code == HTTPStatus.OK
        assert mock_search_users.called is True
        assert response.context["form"].is_valid() is True
        assert response.context["results"] == results

    @patch("utils.sso.SSOClient.search_users")
    @patch("utils.api.resources.APIResource.patch")
    def test_add_user(self, mock_patch, mock_search_users):
        response = self.client.post(
            reverse("users:add_user"),
            data={
                "user_id": "3fbe6479-b9bd-4658-81d7-f07c2a73d33d",
                "user_full_name": "Douglas Miller",
                "action": "add",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id="3fbe6479-b9bd-4658-81d7-f07c2a73d33d",
            groups=[]
        )

    @patch("utils.sso.SSOClient.search_users")
    @patch("utils.api.resources.APIResource.patch")
    def test_add_user_to_group(self, mock_patch, mock_search_users):
        add_user_url = reverse("users:add_user")
        response = self.client.post(
            f"{add_user_url}?group=2",
            data={
                "user_id": "3fbe6479-b9bd-4658-81d7-f07c2a73d33d",
                "user_full_name": "Douglas Miller",
                "action": "add",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id="3fbe6479-b9bd-4658-81d7-f07c2a73d33d",
            groups=[{"id": "2"}]
        )

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.list")
    @patch("utils.api.resources.APIResource.patch")
    def test_change_role(self, mock_patch, mock_list, mock_get):
        mock_get.return_value = User({
            "id": 75,
            "first_name": "Dave",
            "groups": [{"id": 2, "name": "Editor"}]
        })
        mock_list.return_value = [
            PermissionGroup({"id": 1, "name": "Sifter"}),
            PermissionGroup({"id": 2, "name": "Editor"}),
            PermissionGroup({"id": 3, "name": "Publisher"}),
        ]
        response = self.client.post(
            reverse("users:edit_user", kwargs={"user_id": 75}),
            data={"permission_group": "3"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id="75",
            groups=[{"id": "3"}]
        )

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.list")
    @patch("utils.api.resources.APIResource.patch")
    def test_remove_role(self, mock_patch, mock_list, mock_get):
        mock_get.return_value = User({
            "id": 75,
            "first_name": "Dave",
            "groups": [{"id": 2, "name": "Editor"}]
        })
        mock_list.return_value = [
            PermissionGroup({"id": 1, "name": "Sifter"}),
            PermissionGroup({"id": 2, "name": "Editor"}),
            PermissionGroup({"id": 3, "name": "Publisher"}),
        ]
        response = self.client.post(
            reverse("users:edit_user", kwargs={"user_id": 75}),
            data={"permission_group": "0"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id="75",
            groups=[]
        )
