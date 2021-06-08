from http import HTTPStatus

from django.urls import reverse
from unittest.mock import patch

from core.tests import MarketAccessTestCase


class EditWTOStatusTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.APIResource.patch")
    def test_empty_wto_has_been_notified_error(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_wto_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "wto_has_been_notified" in form.errors
        assert "wto_should_be_notified" not in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_empty_wto_should_be_notified_error(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_wto_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"wto_has_been_notified": "no"},
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "wto_has_been_notified" not in form.errors
        assert "wto_should_be_notified" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_success_wto_has_been_notified(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_wto_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"wto_has_been_notified": "yes"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            wto_profile={
                "wto_has_been_notified": True,
                "wto_should_be_notified": None,
            },
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_success_should_be_notified(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_wto_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"wto_has_been_notified": "no", "wto_should_be_notified": "yes"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            wto_profile={
                "wto_has_been_notified": False,
                "wto_should_be_notified": True,
            },
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_success_should_not_be_notified(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_wto_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"wto_has_been_notified": "no", "wto_should_be_notified": "no"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            wto_profile={
                "wto_has_been_notified": False,
                "wto_should_be_notified": False,
            },
        )
