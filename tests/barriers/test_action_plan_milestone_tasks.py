from http import HTTPStatus
from unittest import skip
from unittest.mock import Mock, patch

from django.urls import reverse

from core.tests import MarketAccessTestCase


class ActionPlanMilestoneTasksTestCase(MarketAccessTestCase):
    # N.B. The things called "Objectives" in the UI are known as "Milestones" in the code
    @skip("Just for now")
    @patch("utils.api.resources.ActionPlanTaskResource.create_task")
    def test_required_milestone_task_fails_validation(self, mock_create_method: Mock):
        mock_create_method.return_value = self.action_plan_task
        url = reverse(
            "barriers:action_plan_add_task",
            kwargs={
                "barrier_id": self.barrier["id"],
                "milestone_id": self.action_plan_milestone.id,
            },
        )
        response = self.client.post(
            url,
            follow=False,
            data={},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        for field_name in form.fields.keys():
            assert field_name in form.errors

    @skip("Just for now")
    @patch("utils.api.resources.ActionPlanMilestoneResource.create_milestone")
    def test_add_milestone(self, mock_create_method: Mock):
        mock_create_method.return_value = self.action_plan_task
        url = reverse(
            "barriers:action_plan_add_task",
            kwargs={
                "barrier_id": self.barrier["id"],
                "milestone_id": self.action_plan_milestone.id,
            },
        )
        form_data = {**self.action_plan_task.data}
        form_data[
            "action_type_category_MULTILATERAL_ENGAGEMENT"
        ] = "MULTILATERAL_ENGAGEMENT"
        response = self.client.post(
            url,
            follow=False,
            data=form_data,
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
