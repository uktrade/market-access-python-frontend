from http import HTTPStatus
from unittest.mock import Mock, patch

from django.urls import reverse

from core.tests import MarketAccessTestCase


class ActionPlanMilestoneTasksTestCase(MarketAccessTestCase):
    # N.B. The things called "Objectives" in the UI are known as "Milestones" in the code

    subform_fields = {
        "action_type_category_SCOPING_AND_RESEARCH": "Dialogue",
        "action_type_category_LOBBYING": "Lobbying by officials",
        "action_type_category_UNILATERAL_INTERVENTIONS": "Technical support to UK",
        "action_type_category_BILATERAL_ENGAGEMENT": "Market liberalisation forums",
        "action_type_category_PLURILATERAL_ENGAGEMENT": "With the EU",
        "action_type_category_MULTILATERAL_ENGAGEMENT": "With OECD",
        "action_type_category_EVENT": "Organised exhibition",
        "action_type_category_WHITEHALL_FUNDING_STREAMS": "Prosperity fund",  # pragma: allowlist secret
        "action_type_category_RESOLUTION_NOT_LEAD_BY_DIT": "Lead by OGDs",
        "action_type_category_OTHER": "",
    }

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

    @patch("utils.api.resources.ActionPlanTaskResource.create_task")
    @patch("utils.sso.SSOClient.search_users")
    def test_add_milestone_task(
        self, mock_search_users_method: Mock, mock_create_method: Mock
    ):
        mock_create_method.return_value = self.action_plan_task
        mock_search_users_method.return_value = [
            {
                "email": self.action_plan_task.assigned_to,
                "user_id": "b44e4818-0c96-4133-99e5-defacf4892bd",
            }
        ]
        url = reverse(
            "barriers:action_plan_add_task",
            kwargs={
                "barrier_id": self.barrier["id"],
                "milestone_id": self.action_plan_milestone.id,
            },
        )
        form_data = {**self.action_plan_task.data}
        # We're supposed to be adding a new task, so don't set the id
        form_data.pop("id")
        # Bunch of extra stuff needed for SubformFields
        form_data.update(self.subform_fields)
        # and the asigned stakeholders would be just their id when submitted
        form_data["assigned_stakeholders"] = [
            stakeholder["id"] for stakeholder in form_data["assigned_stakeholders"]
        ]
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

    @patch("utils.api.resources.ActionPlanTaskResource.create_task")
    @patch("utils.sso.SSOClient.search_users")
    def test_update_milestone_task_changed_completion_date_fails_if_reason_not_given(
        self, mock_search_users_method: Mock, mock_create_method: Mock
    ):
        mock_create_method.return_value = self.action_plan_task
        mock_search_users_method.return_value = [
            {
                "email": self.action_plan_task.assigned_to,
                "user_id": "b44e4818-0c96-4133-99e5-defacf4892bd",
            }
        ]
        url = reverse(
            "barriers:action_plan_edit_task",
            kwargs={
                "barrier_id": self.barrier["id"],
                "milestone_id": self.action_plan_milestone.id,
                "id": self.action_plan_task.id,
            },
        )
        form_data = {**self.action_plan_task.data}
        form_data["completion_date"] = "2023-12-12"
        # Bunch of extra stuff needed for SubformFields
        form_data.update(self.subform_fields)
        # and the asigned stakeholders would be just their id when submitted
        form_data["assigned_stakeholders"] = [
            stakeholder["id"] for stakeholder in form_data["assigned_stakeholders"]
        ]
        # Ensure no reason given
        form_data.pop("reason_for_completion_date_change", None)
        response = self.client.post(
            url,
            follow=False,
            data=form_data,
        )
        assert response.status_code == HTTPStatus.OK
        assert "reason_for_completion_date_change" in response.context["form"].errors

    @patch("utils.api.resources.ActionPlanTaskResource.create_task")
    @patch("utils.sso.SSOClient.search_users")
    def test_update_milestone_task_changed_completion_date_succeeds_if_reason_given(
        self, mock_search_users_method: Mock, mock_create_method: Mock
    ):
        mock_create_method.return_value = self.action_plan_task
        mock_search_users_method.return_value = [
            {
                "email": self.action_plan_task.assigned_to,
                "user_id": "b44e4818-0c96-4133-99e5-defacf4892bd",
            }
        ]
        url = reverse(
            "barriers:action_plan_edit_task",
            kwargs={
                "barrier_id": self.barrier["id"],
                "milestone_id": self.action_plan_milestone.id,
                "id": self.action_plan_task.id,
            },
        )
        form_data = {**self.action_plan_task.data}
        form_data["completion_date"] = "2023-12-12"
        # Bunch of extra stuff needed for SubformFields
        form_data.update(self.subform_fields)
        # and the asigned stakeholders would be just their id when submitted
        form_data["assigned_stakeholders"] = [
            stakeholder["id"] for stakeholder in form_data["assigned_stakeholders"]
        ]
        # Ensure no reason given
        form_data["reason_for_completion_date_change"] = "A reason."
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

    @patch("utils.api.resources.ActionPlanTaskResource.create_task")
    @patch("utils.sso.SSOClient.search_users")
    def test_update_milestone_task_unchanged_completion_date_needs_no_reason(
        self, mock_search_users_method: Mock, mock_create_method: Mock
    ):
        mock_create_method.return_value = self.action_plan_task
        mock_search_users_method.return_value = [
            {
                "email": self.action_plan_task.assigned_to,
                "user_id": "b44e4818-0c96-4133-99e5-defacf4892bd",
            }
        ]
        url = reverse(
            "barriers:action_plan_edit_task",
            kwargs={
                "barrier_id": self.barrier["id"],
                "milestone_id": self.action_plan_milestone.id,
                "id": self.action_plan_task.id,
            },
        )
        form_data = {**self.action_plan_task.data}
        # Bunch of extra stuff needed for SubformFields
        form_data.update(self.subform_fields)
        # and the asigned stakeholders would be just their id when submitted
        form_data["assigned_stakeholders"] = [
            stakeholder["id"] for stakeholder in form_data["assigned_stakeholders"]
        ]
        # Ensure no reason given
        form_data.pop("reason_for_completion_date_change", None)
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
