from http import HTTPStatus

from django.urls import reverse
from mock import patch

from core.tests import MarketAccessTestCase


class TestEconomicImpactAssessments(MarketAccessTestCase):
    assessment_id = "08410280-b342-4fe1-9f24-13b8df508e25"

    @patch("utils.api.resources.APIResource.create")
    def test_add_economic_impact_assessment(self, mock_create):
        response = self.client.post(
            reverse(
                "barriers:add_economic_impact_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "impact": "3",
                "explanation": "Explanation...",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_create.assert_called_with(
            economic_assessment_id=15,
            impact="3",
            barrier_id="3e12dd72-8b51-43ec-8269-a173031a0eee",
            explanation="Explanation...",
        )

    @patch("utils.api.resources.APIResource.create")
    def test_add_economic_impact_assessment_errors(self, mock_create):
        response = self.client.post(
            reverse(
                "barriers:add_economic_impact_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "impact": "",
                "explanation": "",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "impact" in form.errors
        assert "explanation" in form.errors
        assert mock_create.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_archive_economic_impact_assessment(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:archive_economic_impact_assessment",
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
    def test_archive_economic_impact_assessment_exit(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:archive_economic_impact_assessment",
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
    def test_economic_impact_assessment_permissions_general_user(self, mock_user):
        mock_user.return_value = self.general_user

        response = self.client.get(
            reverse(
                "barriers:add_economic_impact_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

        response = self.client.get(
            reverse(
                "barriers:archive_economic_impact_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                },
            ),
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    @patch("utils.api.resources.UsersResource.get_current")
    def test_economic_impact_assessment_permissions_analyst(self, mock_user):
        mock_user.return_value = self.analyst_user

        response = self.client.get(
            reverse(
                "barriers:add_economic_impact_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.OK

        response = self.client.get(
            reverse(
                "barriers:archive_economic_impact_assessment",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "assessment_id": self.assessment_id,
                },
            ),
        )
        assert response.status_code == HTTPStatus.OK
