import logging
from http import HTTPStatus
from unittest.mock import patch

import pytest
from django.urls import reverse

from core.tests import MarketAccessTestCase
from users.models import Group, User
from utils.models import ModelList

logger = logging.getLogger(__name__)


class ManageUsersPermissionsTestCase(MarketAccessTestCase):
    def test_link_appears_for_superuser(self):
        response = self.client.get(reverse("reports:new_report"))
        assert response.status_code == HTTPStatus.OK
        html = response.content.decode("utf8")
        assert "Administer users" in html

    @patch("utils.api.resources.UsersResource.get_current")
    def test_link_appears_for_administrator(self, mock_user):
        mock_user.return_value = self.administrator
        response = self.client.get(reverse("reports:new_report"))
        assert response.status_code == HTTPStatus.OK
        html = response.content.decode("utf8")
        assert "Administer users" in html

    @patch("utils.api.resources.UsersResource.get_current")
    def test_link_does_not_appear_for_general_user(self, mock_user):
        mock_user.return_value = self.general_user
        response = self.client.get(reverse("reports:new_report"))
        assert response.status_code == HTTPStatus.OK
        html = response.content.decode("utf8")
        assert "Administer users" not in html

    @patch("utils.api.resources.APIResource.list")
    def test_superuser_can_access_manage_users(self, mock_list):
        response = self.client.get(reverse("users:manage_users"))
        assert response.status_code == HTTPStatus.OK

    @patch("utils.api.resources.GroupsResource.list")
    @patch("utils.api.resources.UsersResource.get_current")
    def test_administrator_can_access_manage_users(self, mock_user, mock_list):
        mock_user.return_value = self.administrator
        response = self.client.get(reverse("users:manage_users"))
        assert response.status_code == HTTPStatus.OK

    @patch("utils.api.resources.UsersResource.get_current")
    def test_general_user_cannot_access_manage_users(self, mock_user):
        mock_user.return_value = self.general_user
        response = self.client.get(reverse("users:manage_users"))
        assert response.status_code == HTTPStatus.FORBIDDEN


class ManageUsersTestCase(MarketAccessTestCase):
    editor = User(
        {"id": 75, "first_name": "Dave", "groups": [{"id": 2, "name": "Editor"}]}
    )

    @patch("utils.sso.SSOClient.search_users")
    def test_no_results(self, mock_search_users):
        mock_search_users.return_value = []
        response = self.client.post(reverse("users:add_user"))
        assert response.status_code == HTTPStatus.OK
        assert mock_search_users.called is True
        assert response.context["form"].is_valid() is True
        assert response.context["results"] == []

    @patch("utils.sso.SSOClient.search_users")
    def test_get_users_results(self, mock_search_users):
        results = [
            {
                "user_id": "3fbe6479-b9bd-4658-81d7-f07c2a73d33d",
                "first_name": "Joseph",
                "last_name": "Heller",
                "email": "bob_bobson1986@hotmail.com",
            }
        ]
        mock_search_users.return_value = results
        response = self.client.get(
            reverse("users:get_users"),
            data={"q": "Hell"},
        )
        assert response.status_code == HTTPStatus.OK
        assert mock_search_users.called is True
        self.assertEqual(
            response.json(),
            {
                "count": 1,
                "results": results,
            },
        )

    @patch("utils.sso.SSOClient.search_users")
    def test_get_users_results_no_results(self, mock_search_users):
        results = []
        mock_search_users.return_value = results
        response = self.client.get(
            reverse("users:get_users"),
            data={"q": "wrong test"},
        )
        assert response.status_code == HTTPStatus.OK
        assert mock_search_users.called is True
        self.assertEqual(response.json(), {"count": 0, "results": results})

    @patch("utils.sso.SSOClient.search_users")
    def test_get_users_results_no_sarch(self, mock_search_users):
        results = [
            {
                "user_id": "3fbe6479-b9bd-4658-81d7-f07c2a73d33d",
                "first_name": "Joseph",
                "last_name": "Heller",
                "email": "bob_bobson1986@hotmail.com",
            }
        ]
        mock_search_users.return_value = results
        response = self.client.get(
            reverse("users:get_users"),
            data={"wrong value": "wrong test"},
        )
        assert response.status_code == HTTPStatus.OK
        assert mock_search_users.called is False
        self.assertEqual(response.json(), {"count": 0, "results": []})

    @patch("utils.api.resources.APIResource.list")
    def test_inactive_users_excluded(self, mock_list):
        mock_list.return_value = ModelList(
            model=User,
            data=[
                {
                    "id": 75,
                    "full_name": "Timmy",
                    "groups": [{"id": 2, "name": "Editor"}],
                    "email": "tim@hotmail.com",
                    "is_active": False,
                },
                {
                    "id": 76,
                    "full_name": "Jimmy",
                    "groups": [{"id": 2, "name": "Editor"}],
                    "email": "jim@hotmail.com",
                    "is_active": True,
                },
            ],
            total_count=2,
        )
        response = self.client.get(reverse("users:manage_users"))
        assert response.status_code == HTTPStatus.OK
        assert mock_list.called is True

        self.assertIn("'is_active': True", str(response.context_data["users"]))
        self.assertNotIn("'is_active': False", str(response.context_data["users"]))

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

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.sso.SSOClient.search_users")
    @patch("utils.api.resources.APIResource.patch")
    def test_add_user(self, mock_patch, mock_search_users, mock_get):
        mock_get.return_value = self.editor
        response = self.client.post(
            reverse("users:add_user"),
            data={
                "user_id": "3fbe6479-b9bd-4658-81d7-f07c2a73d33d",
                "user_full_name": "Douglas Miller",
                "action": "add",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_get.assert_called_with(
            id="3fbe6479-b9bd-4658-81d7-f07c2a73d33d",
        )
        assert mock_patch.called is False

    @patch("utils.sso.SSOClient.search_users")
    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.APIResource.list")
    @patch("utils.api.resources.APIResource.get")
    @pytest.mark.skip(
        reason="Hotfix needs to be deployed. Mocking of functionality seems "
        "problematic and will be included in a follow up PR"
    )
    def test_add_user_to_group(
        self, mock_patch, mock_search_users, mock_list, mock_get
    ):
        mock_patch.return_value = self.editor
        mock_get.return_value = self.editor
        mock_list.return_value = [
            Group({"id": 1, "name": "Sifter"}),
            Group({"id": 2, "name": "Editor"}),
            Group({"id": 3, "name": "Publisher"}),
        ]
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
        mock_list.assert_called_with(id=1)
        mock_patch.assert_called_with(
            id="3fbe6479-b9bd-4658-81d7-f07c2a73d33d", groups=[{"id": 2}]
        )

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.list")
    @patch("utils.api.resources.APIResource.patch")
    def test_change_role(self, mock_patch, mock_list, mock_get):
        mock_patch.return_value = self.editor
        mock_get.return_value = self.editor
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
        mock_patch.assert_called_with(id="75", groups=[{"id": "3"}])

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.GroupsResource.list")
    @patch("utils.api.resources.APIResource.patch")
    def test_change_role_additional_permissions(self, mock_patch, mock_list, mock_get):
        mock_patch.return_value = self.editor
        mock_get.return_value = self.editor
        mock_list.return_value = [
            Group({"id": 1, "name": "Sifter"}),
            Group({"id": 2, "name": "Editor"}),
            Group({"id": 3, "name": "Download approved user"}),
        ]
        response = self.client.post(
            reverse("users:edit_user", kwargs={"user_id": 75}),
            data={
                "group": "2",
                "additional_permissions": "3",
            },
        )
        assert response.status_code == HTTPStatus.FOUND

        mock_patch.assert_called_with(id="75", groups=[{"id": "2"}, {"id": "3"}])

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.GroupsResource.list")
    @patch("utils.api.resources.APIResource.patch")
    def test_make_regional_lead(self, mock_patch, mock_list, mock_get):
        mock_patch.return_value = self.editor
        mock_get.return_value = self.editor
        mock_list.return_value = [
            Group({"id": 1, "name": "Sifter"}),
            Group({"id": 2, "name": "Editor"}),
            Group({"id": 3, "name": "Download approved user"}),
            Group({"id": 4, "name": "Regional Lead - Europe"}),
        ]
        response = self.client.post(
            reverse("users:edit_user", kwargs={"user_id": 75}),
            data={
                "group": "2",
                "additional_permissions": "3",
                "regional_lead_groups": "4",
            },
        )
        assert response.status_code == HTTPStatus.FOUND

        mock_patch.assert_called_with(
            id="75", groups=[{"id": "2"}, {"id": "3"}, {"id": "4"}]
        )

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.list")
    @patch("utils.api.resources.APIResource.patch")
    def test_remove_role(self, mock_patch, mock_list, mock_get):
        mock_patch.return_value = self.editor
        mock_get.return_value = self.editor
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
        mock_patch.assert_called_with(id="75", groups=[])

    @patch("utils.api.resources.APIResource.patch")
    def test_delete_user(self, mock_patch):
        response = self.client.post(
            reverse("users:delete_user", kwargs={"user_id": 56}),
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(id="56", is_active=False, groups=[])
