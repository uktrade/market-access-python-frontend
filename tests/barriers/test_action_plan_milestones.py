from http import HTTPStatus

from django.urls import reverse
from unittest.mock import Mock, patch

from core.tests import MarketAccessTestCase


class ActionPlanMilestonesTestCase(MarketAccessTestCase):
    # N.B. The things called "Objectives" in the UI are known as "Milestones" in the code

    @patch("utils.api.resources.ActionPlanMilestoneResource.create_milestone")
    def test_required_milestone_objective_fails_validation(
        self, mock_create_method: Mock
    ):
        mock_create_method.return_value = self.action_plan_milestone
        url = reverse(
            "barriers:action_plan_add_milestone",
            kwargs={"barrier_id": self.barrier["id"]},
        )
        response = self.client.post(
            url,
            follow=False,
            data={},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert "objective" in form.errors

    @patch("utils.api.resources.ActionPlanMilestoneResource.create_milestone")
    def test_add_milestone(self, mock_create_method: Mock):
        mock_create_method.return_value = self.action_plan_milestone
        url = reverse(
            "barriers:action_plan_add_milestone",
            kwargs={"barrier_id": self.barrier["id"]},
        )
        response = self.client.post(
            url,
            follow=False,
            data={"objective": self.action_plan_milestone.objective},
        )
        expected_url = reverse(
            "barriers:action_plan",
            kwargs={
                "barrier_id": self.barrier["id"],
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert "Location" in response
        assert response["Location"] == expected_url
