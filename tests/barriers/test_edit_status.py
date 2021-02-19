from http import HTTPStatus

from django.urls import reverse
from mock import patch

from core.tests import MarketAccessTestCase


class EditStatusTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.APIResource.patch")
    def test_empty_errors(self, mock_patch):
        response = self.client.post(
            reverse("barriers:edit_status", kwargs={"barrier_id": self.barrier["id"]}),
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "status_summary" in form.errors
        assert "status_date" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_future_date_error(self, mock_patch):
        response = self.client.post(
            reverse("barriers:edit_status", kwargs={"barrier_id": self.barrier["id"]}),
            data={
                "status_date_0": "5",
                "status_date_1": "2050",
                "status_summary": "Test summary",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "status_summary" not in form.errors
        assert "status_date" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_bad_date_error(self, mock_patch):
        response = self.client.post(
            reverse("barriers:edit_status", kwargs={"barrier_id": self.barrier["id"]}),
            data={
                "status_date_0": "1",
                "status_date_1": "20xx",
                "status_summary": "Test resolved summary",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "status_summary" not in form.errors
        assert "status_date" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_success(self, mock_patch):
        response = self.client.post(
            reverse("barriers:edit_status", kwargs={"barrier_id": self.barrier["id"]}),
            data={
                "status_date_0": "1",
                "status_date_1": "2020",
                "status_summary": "Test summary",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            status_date="2020-01-01",
            status_summary="Test summary",
        )
