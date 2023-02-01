from http import HTTPStatus
from unittest.mock import Mock, patch

from django.urls import reverse

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

    @patch("utils.api.resources.ActionPlanMilestoneResource.delete_milestone")
    def test_delete_milestone(self, mock_delete_method: Mock):
        mock_delete_method.return_value = True

        barrier_id = self.barrier["id"]

        url = reverse(
            "barriers:action_plan_delete_milestone",
            kwargs={
                "barrier_id": barrier_id,
                "milestone_id": self.action_plan_milestone.id,
            },
        )
        response = self.client.post(
            url,
        )

        assert response.status_code == 302
        assert response.url == f"/barriers/{barrier_id}/action_plan"

        assert mock_delete_method.call_args[0][0] == barrier_id
        assert mock_delete_method.call_args[0][1] == self.action_plan_milestone.id
