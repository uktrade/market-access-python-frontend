from http import HTTPStatus

from django.urls import reverse
from mock import patch

from barriers.models import EconomicAssessment
from core.tests import MarketAccessTestCase


class TestEconomicAssessments(MarketAccessTestCase):
    assessment_id = 15

    @patch("utils.api.resources.APIResource.patch")
    def test_add_trade_category(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:add_economic_assessment",
                kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"trade_category": "GOODS"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            trade_category="GOODS",
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_add_trade_category_errors(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:add_economic_assessment",
                kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"trade_category": "",},
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "trade_category" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.create")
    def test_add_economic_assessment_data(self, mock_create):
        mock_create.return_value = EconomicAssessment({"id": 55})
        response = self.client.post(
            reverse(
                "barriers:add_economic_assessment_data",
                kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"analysis_data": "Data"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_create.assert_called_with(
            barrier_id=self.barrier["id"],
            analysis_data="Data",
        )

    @patch("utils.api.resources.APIResource.create")
    def test_add_economic_assessment_data_errors(self, mock_create):
        response = self.client.post(
            reverse(
                "barriers:add_economic_assessment_data",
                kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"analysis_data": "",},
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "analysis_data" in form.errors
        assert mock_create.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_update_economic_assessment_rating(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_economic_assessment_rating",
                kwargs={"barrier_id": self.barrier["id"], "assessment_id": self.assessment_id}
            ),
            data={"rating": "HIGH", "explanation": "Explanation"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.assessment_id,
            rating="HIGH",
            explanation="Explanation",
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_update_economic_assessment_rating_errors(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_economic_assessment_rating",
                kwargs={"barrier_id": self.barrier["id"], "assessment_id": self.assessment_id}
            ),
            data={"rating": "",},
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "rating" in form.errors
        assert "explanation" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_approve_economic_assessment(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_economic_assessment_rating",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
            data={
                "rating": "HIGH",
                "explanation": "New explanation...",
                "approved": "True",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.assessment_id,
            rating="HIGH",
            explanation="New explanation...",
            approved=True,
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_reject_economic_assessment(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_economic_assessment_rating",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
            data={
                "rating": "LOW",
                "explanation": "New explanation...",
                "approved": "False",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.assessment_id,
            rating="LOW",
            explanation="New explanation...",
            approved=False,
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_archive_economic_assessment(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:archive_economic_assessment",
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
    def test_archive_economic_assessment_exit(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:archive_economic_assessment",
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
    def test_economic_assessment_permissions_general_user(self, mock_user):
        mock_user.return_value = self.general_user

        response = self.client.get(
            reverse(
                "barriers:add_economic_assessment_data",
                kwargs={"barrier_id": self.barrier["id"]}
            ),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        response = self.client.get(
            reverse(
                "barriers:edit_economic_assessment_data",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        response = self.client.get(
            reverse(
                "barriers:edit_economic_assessment_rating",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        response = self.client.get(
            reverse(
                "barriers:automate_economic_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                }
            ),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        response = self.client.get(
            reverse(
                "barriers:archive_economic_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    @patch("utils.api.resources.UsersResource.get_current")
    def test_economic_assessment_permissions_analyst(self, mock_user):
        mock_user.return_value = self.analyst_user

        response = self.client.get(
            reverse(
                "barriers:add_economic_assessment_data",
                kwargs={"barrier_id": self.barrier["id"]}
            ),
        )
        assert response.status_code == HTTPStatus.OK

        response = self.client.get(
            reverse(
                "barriers:edit_economic_assessment_data",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
        )
        assert response.status_code == HTTPStatus.OK

        response = self.client.get(
            reverse(
                "barriers:edit_economic_assessment_rating",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
        )
        assert response.status_code == HTTPStatus.OK

        response = self.client.get(
            reverse(
                "barriers:automate_economic_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                }
            ),
        )
        assert response.status_code == HTTPStatus.OK

        response = self.client.get(
            reverse(
                "barriers:archive_economic_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                }
            ),
        )
        assert response.status_code == HTTPStatus.OK
