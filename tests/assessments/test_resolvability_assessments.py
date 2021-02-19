from http import HTTPStatus

from django.urls import reverse
from mock import patch

from core.tests import MarketAccessTestCase


class TestResolvabilityAssessments(MarketAccessTestCase):
    assessment_id = "1181e104-4607-4231-b70e-b3f96ccf402f"

    @patch("utils.api.resources.APIResource.create")
    def test_add_resolvability_assessment(self, mock_create):
        response = self.client.post(
            reverse(
                "barriers:add_resolvability_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "time_to_resolve": "3",
                "effort_to_resolve": "4",
                "explanation": "Explanation...",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_create.assert_called_with(
            barrier_id=self.barrier["id"],
            time_to_resolve="3",
            effort_to_resolve="4",
            explanation="Explanation...",
        )

    @patch("utils.api.resources.APIResource.create")
    def test_add_resolvability_assessment_errors(self, mock_create):
        response = self.client.post(
            reverse(
                "barriers:add_resolvability_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "time_to_resolve": "xxx",
                "effort_to_resolve": "",
                "explanation": "",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "time_to_resolve" in form.errors
        assert "effort_to_resolve" in form.errors
        assert "explanation" in form.errors
        assert mock_create.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_update_resolvability_assessment(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_resolvability_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                },
            ),
            data={
                "time_to_resolve": "1",
                "effort_to_resolve": "0",
                "explanation": "New explanation...",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.assessment_id,
            time_to_resolve="1",
            effort_to_resolve="0",
            explanation="New explanation...",
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_update_resolvability_assessment_errors(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_resolvability_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                },
            ),
            data={
                "time_to_resolve": "1",
                "effort_to_resolve": "12",
                "explanation": "",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "time_to_resolve" not in form.errors
        assert "effort_to_resolve" in form.errors
        assert "explanation" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_approve_resolvability_assessment(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_resolvability_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                },
            ),
            data={
                "time_to_resolve": "1",
                "effort_to_resolve": "0",
                "explanation": "New explanation...",
                "approved": "True",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.assessment_id,
            time_to_resolve="1",
            effort_to_resolve="0",
            explanation="New explanation...",
            approved=True,
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_reject_resolvability_assessment(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_resolvability_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                },
            ),
            data={
                "time_to_resolve": "1",
                "effort_to_resolve": "0",
                "explanation": "New explanation...",
                "approved": "False",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.assessment_id,
            time_to_resolve="1",
            effort_to_resolve="0",
            explanation="New explanation...",
            approved=False,
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_archive_resolvability_assessment(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:archive_resolvability_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                },
            ),
            data={
                "are_you_sure": "yes",
                "archived_reason": "Some reason",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.assessment_id,
            archived=True,
            archived_reason="Some reason",
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_archive_resolvability_assessment_exit(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:archive_resolvability_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                },
            ),
            data={
                "are_you_sure": "no",
                "archived_reason": "Some reason",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_patch.called is False

    @patch("utils.api.resources.UsersResource.get_current")
    def test_resolvability_assessment_permissions_general_user(self, mock_user):
        mock_user.return_value = self.general_user

        response = self.client.get(
            reverse(
                "barriers:add_resolvability_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        response = self.client.get(
            reverse(
                "barriers:edit_resolvability_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                },
            ),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        response = self.client.get(
            reverse(
                "barriers:archive_resolvability_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                },
            ),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    @patch("utils.api.resources.UsersResource.get_current")
    def test_resolvability_assessment_permissions_approver(self, mock_user):
        mock_user.return_value = self.approver_user

        response = self.client.get(
            reverse(
                "barriers:add_resolvability_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.OK

        response = self.client.get(
            reverse(
                "barriers:edit_resolvability_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                },
            ),
        )
        assert response.status_code == HTTPStatus.OK

        response = self.client.get(
            reverse(
                "barriers:archive_resolvability_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                },
            ),
        )
        assert response.status_code == HTTPStatus.OK
