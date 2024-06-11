from http import HTTPStatus
from unittest.mock import Mock, patch

from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed

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
    def test_required_fields_lacking_values_fail_validation(
        self, mock_create_method: Mock
    ):
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
        required_field_names = [
            field_name
            for field_name in form.fields.keys()
            if form.fields[field_name].required
        ]
        for field_name in required_field_names:
            assert field_name in form.errors

    @patch("utils.api.resources.ActionPlanTaskResource.create_task")
    @patch("utils.sso.SSOClient.get_user_by_email")
    def test_create_milestone_task_succeeds(
        self, mock_get_user_by_email_method: Mock, mock_create_method: Mock
    ):
        mock_create_method.return_value = self.action_plan_task
        mock_get_user_by_email_method.return_value = {
            "email": self.action_plan_task.assigned_to,
            "user_id": "b44e4818-0c96-4133-99e5-defacf4892bd",
        }

        url = reverse(
            "barriers:action_plan_add_task",
            kwargs={
                "barrier_id": self.barrier["id"],
                "milestone_id": self.action_plan_milestone.id,
            },
        )
        form_data = {**self.action_plan_task.data}
        form_data.update(**self.subform_fields)
        form_data["action_plan"] = self.action_plans
        # The assigned stakeholders would be just their id when submitted
        form_data["assigned_stakeholders"] = [
            stakeholder["id"] for stakeholder in form_data["assigned_stakeholders"]
        ]

        # We're supposed to be adding a new task, so don't set the id
        form_data.pop("id")
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

    @patch("utils.api.resources.ActionPlanTaskResource.update_task")
    @patch("utils.sso.SSOClient.get_user_by_email")
    def test_changed_completion_date_shows_page_asking_for_reason(
        self, mock_get_user_by_email_method: Mock, mock_update_method: Mock
    ):
        mock_update_method.return_value = self.action_plan_task
        mock_get_user_by_email_method.return_value = {
            "email": self.action_plan_task.assigned_to,
            "user_id": "b44e4818-0c96-4133-99e5-defacf4892bd",
        }

        url = reverse(
            "barriers:action_plan_edit_task",
            kwargs={
                "barrier_id": self.barrier["id"],
                "milestone_id": self.action_plan_milestone.id,
                "id": self.action_plan_task.id,
            },
        )
        form_data = {**self.action_plan_task.data}
        form_data.update(**self.subform_fields)
        # The assigned stakeholders would be just their id when submitted
        form_data["assigned_stakeholders"] = [
            stakeholder["id"] for stakeholder in form_data["assigned_stakeholders"]
        ]

        form_data[
            "completion_date"
        ] = "2023-12-12"  # original value in fixture is 2022-12-01
        form_data["completion_date_1"] = "2023"
        form_data["completion_date_0"] = "12"
        response = self.client.post(
            url,
            follow=False,
            data=form_data,
        )
        assert response.status_code == HTTPStatus.OK
        assertTemplateUsed(
            response, "barriers/action_plans/milestone_task_completion_date_reason.html"
        )

    @patch("utils.api.resources.ActionPlanTaskResource.update_task")
    @patch("utils.sso.SSOClient.search_users")
    def test_changed_completion_date_page_insists_upon_being_given_a_reason(
        self, mock_search_users_method: Mock, mock_update_method: Mock
    ):
        mock_update_method.return_value = self.action_plan_task
        mock_search_users_method.return_value = [
            {
                "email": self.action_plan_task.assigned_to,
                "user_id": "b44e4818-0c96-4133-99e5-defacf4892bd",
            }
        ]
        url = reverse(
            "barriers:action_plan_completion_date_change",
            kwargs={
                "barrier_id": self.barrier["id"],
                "milestone_id": self.action_plan_milestone.id,
                "id": self.action_plan_task.id,
            },
        )
        form_data = {**self.action_plan_task.data}
        form_data.update(**self.subform_fields)
        # The assigned stakeholders would be just their id when submitted
        form_data["assigned_stakeholders"] = [
            stakeholder["id"] for stakeholder in form_data["assigned_stakeholders"]
        ]

        form_data[
            "completion_date"
        ] = "2023-12-12"  # original value in fixture is 2022-12-01
        form_data["reason_for_completion_date_change"] = ""
        response = self.client.post(
            url,
            follow=False,
            data=form_data,
        )
        assert response.status_code == HTTPStatus.OK
        assertTemplateUsed(
            response, "barriers/action_plans/milestone_task_completion_date_reason.html"
        )
        assert "reason_for_completion_date_change" in response.context["form"].errors

    @patch("utils.api.resources.ActionPlanTaskResource.update_task")
    @patch("utils.sso.SSOClient.search_users")
    def test_changed_completion_date_succeeds_if_reason_given(
        self, mock_search_users_method: Mock, mock_update_method: Mock
    ):
        mock_update_method.return_value = self.action_plan_task
        mock_search_users_method.return_value = [
            {
                "email": self.action_plan_task.assigned_to,
                "user_id": "b44e4818-0c96-4133-99e5-defacf4892bd",
            }
        ]
        url = reverse(
            "barriers:action_plan_completion_date_change",
            kwargs={
                "barrier_id": self.barrier["id"],
                "milestone_id": self.action_plan_milestone.id,
                "id": self.action_plan_task.id,
            },
        )
        form_data = {**self.action_plan_task.data}
        form_data.update(**self.subform_fields)
        form_data["completion_date"] = "2023-12-12"
        # The assigned stakeholders would be just their id when submitted
        form_data["assigned_stakeholders"] = [
            stakeholder["id"] for stakeholder in form_data["assigned_stakeholders"]
        ]
        # Ensure reason given
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

    @patch("utils.api.resources.ActionPlanTaskResource.update_task")
    @patch("utils.sso.SSOClient.get_user_by_email")
    def test_unchanged_completion_date_needs_no_reason(
        self, mock_get_user_by_email_method: Mock, mock_update_method: Mock
    ):
        mock_update_method.return_value = self.action_plan_task
        mock_get_user_by_email_method.return_value = {
            "email": self.action_plan_task.assigned_to,
            "user_id": "b44e4818-0c96-4133-99e5-defacf4892bd",
        }

        url = reverse(
            "barriers:action_plan_edit_task",
            kwargs={
                "barrier_id": self.barrier["id"],
                "milestone_id": self.action_plan_milestone.id,
                "id": self.action_plan_task.id,
            },
        )
        form_data = {**self.action_plan_task.data}
        form_data.update(**self.subform_fields)
        # The assigned stakeholders would be just their id when submitted
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

    @patch("utils.api.resources.ActionPlanTaskResource.delete_task")
    def test_delete_task(self, mock_delete_method: Mock):
        mock_delete_method.return_value = True

        barrier_id = self.barrier["id"]

        url = reverse(
            "barriers:action_plan_delete_task",
            kwargs={
                "barrier_id": barrier_id,
                "milestone_id": self.action_plan_milestone.id,
                "task_id": self.action_plan_task.id,
            },
        )
        response = self.client.post(
            url,
        )

        assert response.status_code == 302
        assert response.url == f"/barriers/{barrier_id}/action_plan"

        assert mock_delete_method.call_args[0][0] == barrier_id
        assert mock_delete_method.call_args[0][1] == self.action_plan_task.id
