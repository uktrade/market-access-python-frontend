from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from mock import patch


class TeamDetailTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.BarriersResource.get_team_members")
    def test_view(self, mock_get_team_members):
        mock_get_team_members.return_value = self.team_members

        response = self.client.get(
            reverse("barriers:team", kwargs={"barrier_id": self.barrier["id"]})
        )
        assert response.status_code == HTTPStatus.OK
        assert response.context["team_members"] == self.team_members
        assert "barrier" in response.context


class SearchTestCase(MarketAccessTestCase):
    def test_landing_page(self):
        response = self.client.get(
            reverse(
                "barriers:search_team_member", kwargs={"barrier_id": self.barrier["id"]}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context

    @patch("utils.sso.SSOClient.search_users")
    def test_empty_search(self, mock_search_users):
        """
        Empty search should return all users
        """
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
            reverse(
                "barriers:search_team_member", kwargs={"barrier_id": self.barrier["id"]}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert mock_search_users.called is True
        assert response.context["form"].is_valid() is True
        assert response.context["results"] == results

    @patch("utils.sso.SSOClient.search_users")
    def test_no_results(self, mock_search_users):
        mock_search_users.return_value = []
        response = self.client.post(
            reverse(
                "barriers:search_team_member", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"query": "Test search"},
        )
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
            reverse(
                "barriers:search_team_member", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"query": "Test search"},
        )
        assert response.status_code == HTTPStatus.OK
        assert mock_search_users.called is True
        assert response.context["form"].is_valid() is True
        assert response.context["results"] == results


class AddTeamMemberTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.BarriersResource.get_team_members")
    def test_initial_data(self, mock_get_team_members, mock_get_user):
        mock_get_team_members.return_value = self.team_members
        user_id = "c12195ed-bf30-4a67-ba73-e95cfe012f77"
        mock_get_user.return_value = self.users[0]

        response = self.client.get(
            reverse(
                "barriers:add_team_member", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"user": user_id},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.context["user"] == self.users[0]
        assert response.context["form"].initial["user"] == user_id

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.BarriersResource.get_team_members")
    def test_no_user(self, mock_get_team_members, mock_get_user):
        mock_get_team_members.return_value = self.team_members
        mock_get_user.return_value = self.users[0]

        response = self.client.get(
            reverse(
                "barriers:add_team_member", kwargs={"barrier_id": self.barrier["id"]}
            ),
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_get_user.called is False
        assert mock_get_team_members.called is False

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.BarriersResource.get_team_members")
    def test_empty_role(self, mock_get_team_members, mock_get_user):
        mock_get_team_members.return_value = self.team_members
        user_id = "c12195ed-bf30-4a67-ba73-e95cfe012f77"
        mock_get_user.return_value = self.users[0]

        response = self.client.post(
            reverse(
                "barriers:add_team_member", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"user": user_id},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.context["user"] == self.users[0]
        assert "role" in response.context["form"].errors

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.BarriersResource.get_team_members")
    @patch("utils.api.resources.BarriersResource.add_team_member")
    def test_success(
        self, mock_add_team_member, mock_get_team_members, mock_get_user,
    ):
        mock_get_team_members.return_value = self.team_members
        user_id = "c12195ed-bf30-4a67-ba73-e95cfe012f77"
        mock_get_user.return_value = self.users[0]

        response = self.client.post(
            reverse(
                "barriers:add_team_member", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"user": user_id, "role": "Horse"},
        )

        assert response.status_code == HTTPStatus.FOUND
        mock_add_team_member.assert_called_with(
            barrier_id=self.barrier["id"], user_id=user_id, role="Horse",
        )
        assert mock_get_user.called is False
        assert mock_get_team_members.called is False


class DeleteTeamMemberTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.BarriersResource.get_team_members")
    @patch("utils.api.resources.BarriersResource.delete_team_member")
    def test_get(self, mock_delete_team_member, mock_get_team_members):
        mock_get_team_members.return_value = self.team_members
        response = self.client.get(
            reverse(
                "barriers:delete_team_member",
                kwargs={"barrier_id": self.barrier["id"], "team_member_id": 9,},
            ),
        )

        assert response.status_code == HTTPStatus.OK
        assert response.context["team_member"] == self.team_members[0]
        assert mock_delete_team_member.called is False

    @patch("utils.api.resources.BarriersResource.get_team_members")
    @patch("utils.api.resources.BarriersResource.delete_team_member")
    def test_post(self, mock_delete_team_member, mock_get_team_members):
        response = self.client.post(
            reverse(
                "barriers:delete_team_member",
                kwargs={"barrier_id": self.barrier["id"], "team_member_id": 37,},
            ),
        )

        assert response.status_code == HTTPStatus.FOUND
        mock_delete_team_member.assert_called_with(37)
        assert mock_get_team_members.called is False


class ChangeOwnerTestCase(MarketAccessTestCase):

    @patch("utils.api.resources.BarriersResource.get_team_member")
    def test_get(self, mock_get_team_member):
        """
        Details of owner should be added to context so the name can be displayed.
        """
        mock_get_team_member.return_value = self.team_members[0]

        url = reverse(
            "barriers:team_change_owner",
            kwargs={"barrier_id": self.barrier["id"], "team_member_id": 9},
        )
        response = self.client.get(url)

        assert HTTPStatus.OK == response.status_code
        assert response.context["owner"] == self.team_members[0]
        assert mock_get_team_member.called is True

    @patch("utils.sso.SSOClient.search_users")
    @patch("utils.api.resources.BarriersResource.get_team_member")
    def test_search(self, mock_get_team_member, mock_search_users):
        """
        When posting without an action it should attempt to search.
        """
        mock_get_team_member.return_value = self.team_members[0]
        url = reverse(
            "barriers:team_change_owner",
            kwargs={"barrier_id": self.barrier["id"], "team_member_id": 9},
        )
        form_data = {"query": "wobble",}

        response = self.client.post(url, data=form_data)

        assert HTTPStatus.OK == response.status_code
        assert mock_search_users.called is True

    @patch("utils.api.resources.BarriersResource.get_team_members")
    @patch("utils.api.resources.BarriersResource.patch_team_member")
    @patch("utils.api.resources.BarriersResource.get_team_member")
    def test_add_new_owner(self, mock_get_team_member, mock_patch_team_member, mock_get_team_members):
        """
        Should redirect to team page once the owner has been changed.
        """
        mock_get_team_member.return_value = self.team_members[0]
        redirect_url = reverse("barriers:team", kwargs={"barrier_id": self.barrier["id"]})
        url = reverse(
            "barriers:team_change_owner",
            kwargs={"barrier_id": self.barrier["id"], "team_member_id": 9},
        )
        form_data = {
            "action": "add",
            "user_id": "wibble",
            "user_full_name": "wobble",
        }

        response = self.client.post(url, data=form_data)

        self.assertRedirects(response, redirect_url)
        assert mock_patch_team_member.called is True
