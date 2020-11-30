from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from mock import patch


class EditCommercialValueTestCase(MarketAccessTestCase):
    def test_commercial_value_has_initial_data(self):
        response = self.client.get(
            reverse(
                "barriers:edit_commercial_value",
                kwargs={"barrier_id": self.barrier["id"]},
            )
        )

        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["commercial_value"] == self.barrier["commercial_value"]
        assert form.initial["commercial_value_explanation"] == self.barrier["commercial_value_explanation"]

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_commercial_value_calls_api(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_commercial_value",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "commercial_value": "500003",
                "commercial_value_explanation": "Wibble, wobble."
            },
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            commercial_value=500003,
            commercial_value_explanation="Wibble, wobble."
        )
        assert response.status_code == HTTPStatus.FOUND

    @patch("utils.api.resources.APIResource.patch")
    def test_commercial_value_bad_value(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_commercial_value",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"commercial_value": "10-0"},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "commercial_value" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_commercial_value_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_commercial_value",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"commercial_value": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "commercial_value" in form.errors
        assert mock_patch.called is False
