from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase
from users.models import Group, User

from mock import patch


class ManageUsersPermissionsTestCase(MarketAccessTestCase):
    administrator = User(
        {
            "is_superuser": False,
            "is_active": True,
            "permissions": ["change_user", "list_users"],
        }
    )
    general_user = User(
        {
            "is_superuser": False,
            "is_active": True,
            "permissions": [],
        }
    )

    def test_link_appears_for_superuser(self):
        response = self.client.get(reverse("reports:new_report"))
        assert response.status_code == HTTPStatus.OK
        html = response.content.decode('utf8')
        assert "Administer users" in html

    @patch("utils.api.resources.UsersResource.get_current")
    def test_link_appears_for_administrator(self, mock_user):
        mock_user.return_value = self.administrator
        response = self.client.get(reverse("reports:new_report"))
        assert response.status_code == HTTPStatus.OK
        html = response.content.decode('utf8')
        assert "Administer users" in html

    @patch("utils.api.resources.UsersResource.get_current")
    def test_link_does_not_appear_for_general_user(self, mock_user):
        mock_user.return_value = self.general_user
        response = self.client.get(reverse("reports:new_report"))
        assert response.status_code == HTTPStatus.OK
        html = response.content.decode('utf8')
        assert "Administer users" not in html

    def test_superuser_can_access_manage_users(self):
        response = self.client.get(reverse("users:manage_users"))
        assert response.status_code == HTTPStatus.OK

    @patch("utils.api.resources.UsersResource.get_current")
    def test_administrator_can_access_manage_users(self, mock_user):
        mock_user.return_value = self.administrator
        response = self.client.get(reverse("users:manage_users"))
        assert response.status_code == HTTPStatus.OK

    @patch("utils.api.resources.UsersResource.get_current")
    def test_general_user_cannot_access_manage_users(self, mock_user):
        mock_user.return_value = self.general_user
        response = self.client.get(reverse("users:manage_users"))
        assert response.status_code == HTTPStatus.FORBIDDEN


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
            groups=[{"id": 2}]
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
            Group({"id": 1, "name": "Sifter"}),
            Group({"id": 2, "name": "Editor"}),
            Group({"id": 3, "name": "Publisher"}),
        ]
        response = self.client.post(
            reverse("users:edit_user", kwargs={"user_id": 75}),
            data={"group": "3"},
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
            Group({"id": 1, "name": "Sifter"}),
            Group({"id": 2, "name": "Editor"}),
            Group({"id": 3, "name": "Publisher"}),
        ]
        response = self.client.post(
            reverse("users:edit_user", kwargs={"user_id": 75}),
            data={"group": "0"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id="75",
            groups=[]
        )
