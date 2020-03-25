from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from mock import patch


class ArchiveTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.APIResource.patch")
    def test_empty_reason(self, mock_patch):
        response = self.client.post(
            reverse("barriers:archive", kwargs={"barrier_id": self.barrier["id"]})
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "reason" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_duplicate_empty_explanation(self, mock_patch):
        response = self.client.post(
            reverse("barriers:archive", kwargs={"barrier_id": self.barrier["id"]}),
            data={"reason": "DUPLICATE"},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "duplicate_explanation" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_non_a_barrier_empty_explanation(self, mock_patch):
        response = self.client.post(
            reverse("barriers:archive", kwargs={"barrier_id": self.barrier["id"]}),
            data={"reason": "NOT_A_BARRIER"},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "not_a_barrier_explanation" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_other_empty_explanation(self, mock_patch):
        response = self.client.post(
            reverse("barriers:archive", kwargs={"barrier_id": self.barrier["id"]}),
            data={"reason": "OTHER"},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "other_explanation" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_duplicate_success(self, mock_patch):
        response = self.client.post(
            reverse("barriers:archive", kwargs={"barrier_id": self.barrier["id"]}),
            data={"reason": "DUPLICATE", "duplicate_explanation": "Explanation"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            archived=True,
            archived_reason="DUPLICATE",
            archived_explanation="Explanation",
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_not_a_barrier_success(self, mock_patch):
        response = self.client.post(
            reverse("barriers:archive", kwargs={"barrier_id": self.barrier["id"]}),
            data={
                "reason": "NOT_A_BARRIER",
                "not_a_barrier_explanation": "Explanation"
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            archived=True,
            archived_reason="NOT_A_BARRIER",
            archived_explanation="Explanation",
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_other_success(self, mock_patch):
        response = self.client.post(
            reverse("barriers:archive", kwargs={"barrier_id": self.barrier["id"]}),
            data={"reason": "OTHER", "other_explanation": "Other Explanation"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            archived=True,
            archived_reason="OTHER",
            archived_explanation="Other Explanation",
        )


class UnarchiveTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.APIResource.patch")
    def test_empty_reason(self, mock_patch):
        response = self.client.post(
            reverse("barriers:unarchive", kwargs={"barrier_id": self.barrier["id"]})
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "reason" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_success(self, mock_patch):
        response = self.client.post(
            reverse("barriers:unarchive", kwargs={"barrier_id": self.barrier["id"]}),
            data={"reason": "Reason for unarchiving"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            archived=False,
            unarchived_reason="Reason for unarchiving",
        )
