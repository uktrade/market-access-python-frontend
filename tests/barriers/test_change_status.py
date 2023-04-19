from http import HTTPStatus

from django.urls import reverse
from mock import patch

from core.tests import MarketAccessTestCase


class ChangeStatusTestCase(MarketAccessTestCase):
    @patch("utils.api.client.BarriersResource.set_status")
    def test_no_status_gets_error(self, mock_set_status):
        response = self.client.post(
            reverse("barriers:change_status", kwargs={"barrier_id": self.barrier["id"]})
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "status" in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_open_in_progress_errors(self, mock_set_status):
        response = self.client.post(
            reverse(
                "barriers:change_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"status": "2"},
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "status" not in form.errors
        assert "open_in_progress_summary" in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_open_in_progress_success(self, mock_set_status):
        response = self.client.post(
            reverse(
                "barriers:change_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={
                "status": "2",
                "open_in_progress_summary": "Test summary",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_set_status.assert_called_with(
            barrier_id=self.barrier["id"],
            status="2",
            status_summary="Test summary",
        )

    @patch("utils.api.client.BarriersResource.set_status")
    def test_partially_resolved_errors(self, mock_set_status):
        self.barrier["status"]["id"] = 2
        response = self.client.post(
            reverse(
                "barriers:change_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"status": "3"},
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "status" not in form.errors
        assert "part_resolved_summary" in form.errors
        assert "part_resolved_date" in form.errors
        assert len(form.errors) == 2
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_partially_resolved_future_date_error(self, mock_set_status):
        response = self.client.post(
            reverse(
                "barriers:change_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={
                "status": "3",
                "part_resolved_date_0": "15",
                "part_resolved_date_1": "5",
                "part_resolved_date_2": "2050",
                "part_resolved_summary": "Part resolved summary",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "status" not in form.errors
        assert "part_resolved_summary" not in form.errors
        assert "part_resolved_date" in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_partially_resolved_bad_date_error(self, mock_set_status):
        response = self.client.post(
            reverse(
                "barriers:change_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={
                "status": "3",
                "part_resolved_date_0": "15",
                "part_resolved_date_1": "5",
                "part_resolved_date_2": "20xx",
                "part_resolved_summary": "Part resolved summary",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "status" not in form.errors
        assert "part_resolved_summary" not in form.errors
        assert "part_resolved_date" in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_partially_resolved_success(self, mock_set_status):
        response = self.client.post(
            reverse(
                "barriers:change_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={
                "status": "3",
                "part_resolved_date_0": "16",
                "part_resolved_date_1": "12",
                "part_resolved_date_2": "2015",
                "part_resolved_summary": "Part resolved summary",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_set_status.assert_called_with(
            barrier_id=self.barrier["id"],
            status="3",
            status_date="2015-12-16",
            status_summary="Part resolved summary",
        )

    @patch("utils.api.client.BarriersResource.set_status")
    def test_fully_resolved_errors(self, mock_set_status):
        self.barrier["status"]["id"] = 2
        response = self.client.post(
            reverse(
                "barriers:change_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"status": "4"},
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "status" not in form.errors
        assert "resolved_summary" in form.errors
        assert "resolved_date" in form.errors
        assert len(form.errors) == 2
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_fully_resolved_future_date_error(self, mock_set_status):
        self.barrier["status"]["id"] = 2
        response = self.client.post(
            reverse(
                "barriers:change_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={
                "status": "4",
                "resolved_date_0": "15",
                "resolved_date_1": "5",
                "resolved_date_2": "2050",
                "resolved_summary": "Test resolved summary",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "status" not in form.errors
        assert "resolved_summary" not in form.errors
        assert "resolved_date" in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_fully_resolved_bad_date_error(self, mock_set_status):
        self.barrier["status"]["id"] = 2
        response = self.client.post(
            reverse(
                "barriers:change_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={
                "status": "4",
                "resolved_date_0": "15",
                "resolved_date_1": "5",
                "resolved_date_2": "20xx",
                "resolved_summary": "Test resolved summary",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "status" not in form.errors
        assert "resolved_summary" not in form.errors
        assert "resolved_date" in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_fully_resolved_success(self, mock_set_status):
        self.barrier["status"]["id"] = 2
        response = self.client.post(
            reverse(
                "barriers:change_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={
                "status": "4",
                "resolved_date_0": "10",
                "resolved_date_1": "5",
                "resolved_date_2": "2019",
                "resolved_summary": "Test resolved summary",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_set_status.assert_called_with(
            barrier_id=self.barrier["id"],
            status="4",
            status_date="2019-05-10",
            status_summary="Test resolved summary",
        )

    @patch("utils.api.client.BarriersResource.set_status")
    def test_dormant_status_errors(self, mock_set_status):
        response = self.client.post(
            reverse(
                "barriers:change_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"status": "5"},
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "status" not in form.errors
        assert "dormant_summary" in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_dormant_status_success(self, mock_set_status):
        response = self.client.post(
            reverse(
                "barriers:change_status", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"status": "5", "dormant_summary": "Test dormant summary"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_set_status.assert_called_with(
            barrier_id=self.barrier["id"],
            status="5",
            status_summary="Test dormant summary",
        )
