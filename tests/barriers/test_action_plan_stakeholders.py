from http import HTTPStatus
from unittest.mock import Mock, patch

from django.urls import reverse

from barriers.constants import (
    ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES,
    ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES,
)
from core.tests import MarketAccessTestCase


class ActionPlanStakeholdersTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.ActionPlanStakeholderResource.create_stakeholder")
    def test_required_stakeholder_type_fails_validation(self, mock_create_method: Mock):
        mock_create_method.return_value = self.action_plan_individual_stakeholder
        url = reverse(
            "barriers:action_plan_stakeholders_add",
            kwargs={"barrier_id": self.barrier["id"]},
        )
        response = self.client.post(
            url,
            follow=False,
            data={},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert "is_organisation" in form.errors

    @patch("utils.api.resources.ActionPlanStakeholderResource.create_stakeholder")
    def test_add_individual_stakeholder(self, mock_create_method: Mock):
        mock_create_method.return_value = self.action_plan_individual_stakeholder
        url = reverse(
            "barriers:action_plan_stakeholders_add",
            kwargs={"barrier_id": self.barrier["id"]},
        )
        response = self.client.post(
            url,
            follow=False,
            data={"is_organisation": ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES.INDIVIDUAL},
        )
        expected_url = reverse(
            "barriers:action_plan_stakeholders_new_individual",
            kwargs={"barrier_id": self.barrier["id"]},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert "Location" in response
        assert response["Location"] == expected_url

    @patch("utils.api.resources.ActionPlanStakeholderResource.create_stakeholder")
    def test_add_organisation_stakeholder(self, mock_create_method: Mock):
        mock_create_method.return_value = self.action_plan_organisation_stakeholder
        url = reverse(
            "barriers:action_plan_stakeholders_add",
            kwargs={"barrier_id": self.barrier["id"]},
        )
        response = self.client.post(
            url,
            follow=False,
            data={"is_organisation": ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES.ORGANISATION},
        )
        expected_url = reverse(
            "barriers:action_plan_stakeholders_new_organisation",
            kwargs={
                "barrier_id": self.barrier["id"],
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert "Location" in response
        assert response["Location"] == expected_url

    @patch("utils.api.resources.ActionPlanStakeholderResource.create_stakeholder")
    def test_add_individual_stakeholder_details(self, mock_update_method: Mock):
        mock_update_method.return_value = self.action_plan_individual_stakeholder
        url = reverse(
            "barriers:action_plan_stakeholders_new_individual",
            kwargs={
                "barrier_id": self.barrier["id"],
            },
        )
        response = self.client.post(
            url,
            follow=False,
            data={
                "name": self.action_plan_individual_stakeholder.name,
                "status": ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES.TARGET,
                "job_title": self.action_plan_individual_stakeholder.job_title,
                "organisation": self.action_plan_individual_stakeholder.organisation,
            },
        )
        expected_url = reverse(
            "barriers:action_plan_stakeholders_list",
            kwargs={"barrier_id": self.barrier["id"]},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert "Location" in response
        assert response["Location"] == expected_url

    @patch("utils.api.resources.ActionPlanStakeholderResource.create_stakeholder")
    def test_required_stakeholder_details_fail_validation(
        self, mock_update_method: Mock
    ):
        mock_update_method.return_value = self.action_plan_organisation_stakeholder
        url = reverse(
            "barriers:action_plan_stakeholders_new_organisation",
            kwargs={
                "barrier_id": self.barrier["id"],
            },
        )
        response = self.client.post(
            url,
            follow=False,
            data={
                "name": "",
                "status": "",
            },
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert "name" in form.errors
        assert "status" in form.errors

    @patch("utils.api.resources.ActionPlanStakeholderResource.create_stakeholder")
    def test_required_individual_stakeholder_details_fail_validation(
        self, mock_update_method: Mock
    ):
        mock_update_method.return_value = self.action_plan_individual_stakeholder
        url = reverse(
            "barriers:action_plan_stakeholders_new_individual",
            kwargs={
                "barrier_id": self.barrier["id"],
            },
        )
        response = self.client.post(
            url,
            follow=False,
            data={
                "name": self.action_plan_individual_stakeholder.name,
                "status": ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES.TARGET,
                "job_title": "",
                "organisation": "",
            },
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert "job_title" in form.errors
        assert "organisation" in form.errors

    @patch("utils.api.resources.ActionPlanStakeholderResource.create_stakeholder")
    def test_add_organisation_stakeholder_details(self, mock_update_method: Mock):
        mock_update_method.return_value = self.action_plan_organisation_stakeholder
        url = reverse(
            "barriers:action_plan_stakeholders_new_organisation",
            kwargs={
                "barrier_id": self.barrier["id"],
            },
        )
        response = self.client.post(
            url,
            follow=False,
            data={
                "name": self.action_plan_organisation_stakeholder.name,
                "status": ACTION_PLAN_STAKEHOLDER_STATUS_CHOICES.TARGET,
            },
        )
        expected_url = reverse(
            "barriers:action_plan_stakeholders_list",
            kwargs={"barrier_id": self.barrier["id"]},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert "Location" in response
        assert response["Location"] == expected_url
