import json
from http import HTTPStatus
from unittest.mock import patch

from django.urls import reverse

from core.tests import MarketAccessTestCase


class AccountHomeViewsTestCase(MarketAccessTestCase):

    @property
    def user_id(self):
        return str(self.current_user.data["id"])

    def test_user_can_access_account(self):
        response = self.client.get(reverse("users:account"))
        assert response.status_code == HTTPStatus.OK

    def test_link(self):
        response = self.client.get(reverse("users:account"))
        assert response.status_code == HTTPStatus.OK
        html = response.content.decode("utf8")
        assert "Account" in html

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_overseas_regions(self, mock_patch):
        """
        Editing overseas regions should call the API
        """
        overseas_regions = [
            "8d4c4f31-06ce-4320-8e2f-1c13559e125f",
            "04a7cff0-03dd-4677-aa3c-12dd8426f0d7",
        ]
        response = self.client.post(
            reverse(
                "users:edit_user_overseas_regions",
            ),
            data={"form": json.dumps(overseas_regions)},
        )
        assert response.status_code == HTTPStatus.FOUND

        mock_patch.assert_called_with(
            id=self.user_id, overseas_regions=sorted(overseas_regions)
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_policy_teams(self, mock_patch):
        """
        Editing policy teams should call the API
        """
        policy_teams = ["1", "2"]
        response = self.client.post(
            reverse(
                "users:edit_user_policy_teams",
            ),
            data={"form": json.dumps(policy_teams)},
        )
        assert response.status_code == HTTPStatus.FOUND

        mock_patch.assert_called_with(
            id=self.user_id, policy_teams=sorted(policy_teams)
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_sectors(self, mock_patch):
        """
        Editing sectors should call the API
        """
        sectors = [
            "af959812-6095-e211-a939-e4115bead28a",
            "9538cecc-5f95-e211-a939-e4115bead28a",
        ]
        response = self.client.post(
            reverse(
                "users:edit_user_sectors",
            ),
            data={"form": json.dumps(sectors)},
        )
        assert response.status_code == HTTPStatus.FOUND

        mock_patch.assert_called_with(id=self.user_id, sectors=sorted(sectors))

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_barrier_locations(self, mock_patch):
        """
        Editing barrier locations should call the API
        """
        trading_blocs = ["TB00003"]
        countries = ["87756b9a-5d95-e211-a939-e4115bead28a"]
        response = self.client.post(
            reverse(
                "users:edit_user_barrier_locations",
            ),
            data={"form": json.dumps(trading_blocs + countries)},
        )
        assert response.status_code == HTTPStatus.FOUND

        mock_patch.assert_called_with(
            id=self.user_id,
            trading_blocs=trading_blocs,
            countries=countries,
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_government_department(self, mock_patch):
        """
        Editing government department should call the API
        """
        department = 1
        response = self.client.post(
            reverse(
                "users:edit_user_government_department",
            ),
            data={"form": department},
        )

        assert response.status_code == HTTPStatus.FOUND

        mock_patch.assert_called_with(
            id=self.user_id,
            organisations=[department],
        )
