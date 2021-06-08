from http import HTTPStatus

from django.urls import reverse
from unittest.mock import patch

from core.tests import MarketAccessTestCase


class EditPublicBarrierTitleTestCase(MarketAccessTestCase):
    def test_edit_title_has_initial_data(self):
        response = self.client.get(
            reverse(
                "barriers:edit_public_barrier_title",
                kwargs={"barrier_id": self.barrier["id"]},
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["title"] == self.public_barrier["title"]

    @patch("utils.api.resources.APIResource.patch")
    def test_title_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_public_barrier_title",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"title": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "title" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_title_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_public_barrier_title",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"title": "New Title"},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            title="New Title",
        )
        assert response.status_code == HTTPStatus.FOUND


class EditPublicBarrierSummaryTestCase(MarketAccessTestCase):
    def test_edit_summary_has_initial_data(self):
        response = self.client.get(
            reverse(
                "barriers:edit_public_barrier_summary",
                kwargs={"barrier_id": self.barrier["id"]},
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["summary"] == self.public_barrier["summary"]

    @patch("utils.api.resources.APIResource.patch")
    def test_summary_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_public_barrier_summary",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"summary": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "summary" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_summary_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_public_barrier_summary",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"summary": "New summary"},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            summary="New summary",
        )
        assert response.status_code == HTTPStatus.FOUND


class EditPublicBarrierEligibilityTestCase(MarketAccessTestCase):
    def test_eligibility_has_initial_data(self):
        response = self.client.get(
            reverse(
                "barriers:edit_public_eligibility",
                kwargs={"barrier_id": self.barrier["id"]},
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert (
            form.initial["public_eligibility"] == "yes"
            if self.barrier["public_eligibility"]
            else "no"
        )
        assert (
            form.initial["allowed_summary"]
            == self.barrier["public_eligibility_summary"]
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_eligibility_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_public_eligibility",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "public_eligibility" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_eligibility_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_public_eligibility",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"public_eligibility": "yes", "allowed_summary": "summary"},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            public_eligibility=True,
            public_eligibility_postponed=False,
            public_eligibility_summary="summary",
        )
        assert response.status_code == HTTPStatus.FOUND


class PublicBarrierActionsTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.PublicBarriersResource.mark_as_ready")
    def test_mark_as_ready_calls_api(self, mock_mark_as_ready):
        response = self.client.post(
            reverse(
                "barriers:public_barrier_detail",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"action": "mark-as-ready"},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_mark_as_ready.called is True

    @patch("utils.api.resources.PublicBarriersResource.publish")
    def test_publish_calls_api(self, mock_publish):
        response = self.client.post(
            reverse(
                "barriers:public_barrier_detail",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"action": "publish"},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_publish.called is True

    @patch("utils.api.resources.PublicBarriersResource.mark_as_in_progress")
    def test_mark_as_in_progress_calls_api(self, mock_mark_as_in_progress):
        response = self.client.post(
            reverse(
                "barriers:public_barrier_detail",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"action": "mark-as-in-progress"},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_mark_as_in_progress.called is True

    @patch("utils.api.resources.PublicBarriersResource.unpublish")
    def test_unpublish_calls_api(self, mock_unpublish):
        response = self.client.post(
            reverse(
                "barriers:public_barrier_detail",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"action": "unpublish"},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_unpublish.called is True

    @patch("utils.api.resources.PublicBarriersResource.ignore_all_changes")
    def test_ignore_changes_calls_api(self, mock_ignore_changes):
        response = self.client.post(
            reverse(
                "barriers:public_barrier_detail",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"action": "ignore-changes"},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_ignore_changes.called is True
