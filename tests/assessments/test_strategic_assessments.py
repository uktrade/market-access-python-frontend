from http import HTTPStatus

from django.urls import reverse
from mock import patch

from core.tests import MarketAccessTestCase


class TestStrategicAssessments(MarketAccessTestCase):
    assessment_id = "5ffabcc8-5f05-4c1a-a7ca-b81834a58cdd"
    form_data = {
        "hmg_strategy": "hmg_strategy test",
        "government_policy": "government_policy test",
        "trading_relations": "trading_relations test",
        "uk_interest_and_security": "uk_interest_and_security test",
        "uk_grants": "uk_grants test",
        "competition": "competition test",
        "additional_information": "additional_information test",
        "scale": "4",
    }

    @patch("utils.api.resources.APIResource.create")
    def test_add_strategic_assessment(self, mock_create):
        response = self.client.post(
            reverse(
                "barriers:add_strategic_assessment",
                kwargs={"barrier_id": self.barrier["id"]}
            ),
            data=self.form_data,
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_create.assert_called_with(
            barrier_id=self.barrier["id"],
            **self.form_data,
        )

    @patch("utils.api.resources.APIResource.create")
    def test_add_strategic_assessment_errors(self, mock_create):
        response = self.client.post(
            reverse(
                "barriers:add_strategic_assessment",
                kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={
                "hmg_strategy": "Valid value",
                "scale": "",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "scale" in form.errors
        assert "government_policy" in form.errors
        assert "trading_relations" in form.errors
        assert "hmg_strategy" not in form.errors
        assert "additional_information" not in form.errors
        assert mock_create.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_update_strategic_assessment(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_strategic_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
            data=self.form_data,
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.assessment_id,
            **self.form_data,
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_update_strategic_assessment_errors(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_strategic_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
            data={
                "government_policy": "Valid value",
                "scale": "55",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "government_policy" not in form.errors
        assert "scale" in form.errors
        assert "uk_interest_and_security" in form.errors
        assert "uk_grants" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_approve_strategic_assessment(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_strategic_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
            data={
                "approved": "True",
                **self.form_data,
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.assessment_id,
            approved=True,
            **self.form_data,
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_reject_strategic_assessment(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_strategic_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
            data={
                "approved": "False",
                **self.form_data,
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.assessment_id,
            approved=False,
            **self.form_data,
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_archive_strategic_assessment(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:archive_strategic_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
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
    def test_archive_strategic_assessment_exit(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:archive_strategic_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
            data={
                "are_you_sure": "no",
                "archived_reason": "Some reason",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_patch.called is False

    @patch("utils.api.resources.UsersResource.get_current")
    def test_strategic_assessment_permissions_general_user(self, mock_user):
        mock_user.return_value = self.general_user

        response = self.client.get(
            reverse(
                "barriers:add_strategic_assessment",
                kwargs={"barrier_id": self.barrier["id"]}
            ),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        response = self.client.get(
            reverse(
                "barriers:edit_strategic_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        response = self.client.get(
            reverse(
                "barriers:archive_strategic_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    @patch("utils.api.resources.UsersResource.get_current")
    def test_strategic_assessment_permissions_approver(self, mock_user):
        mock_user.return_value = self.approver_user

        response = self.client.get(
            reverse(
                "barriers:add_strategic_assessment",
                kwargs={"barrier_id": self.barrier["id"]}
            ),
        )
        assert response.status_code == HTTPStatus.OK

        response = self.client.get(
            reverse(
                "barriers:edit_strategic_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
        )
        assert response.status_code == HTTPStatus.OK

        response = self.client.get(
            reverse(
                "barriers:archive_strategic_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
        )
        assert response.status_code == HTTPStatus.OK
