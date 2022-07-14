from http import HTTPStatus

from django.urls import reverse
from unittest.mock import patch, Mock

from unittest import skip

from barriers.constants import ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES
from core.tests import MarketAccessTestCase


class ActionPlanStakeholdersTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.ActionPlanStakeholderResource.create_stakeholder")
    def test_add_individual_stakeholder(self, mock_create: Mock):
        mock_create.return_value = self.action_plan_individual_stakeholder
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
            "barriers:action_plan_stakeholders_add_details",
            kwargs={
                "barrier_id": self.barrier["id"],
                "id": self.action_plan_individual_stakeholder.id,
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert "Location" in response
        assert response["Location"] == expected_url

    @patch("utils.api.resources.ActionPlanStakeholderResource.create_stakeholder")
    def test_add_organisation_stakeholder(self, mock_create):
        mock_create.return_value = self.action_plan_organisation_stakeholder
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
            "barriers:action_plan_stakeholders_add_details",
            kwargs={
                "barrier_id": self.barrier["id"],
                "id": self.action_plan_organisation_stakeholder.id,
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert "Location" in response
        assert response["Location"] == expected_url

    @skip("WIP")
    @patch("utils.api.resources.ActionPlanStakeholderResource.update_stakeholder")
    def test_add_individual_stakeholder_details(self, mock_create):
        url = reverse(
            "barriers:action_plan_stakeholders_add_details",
            kwargs={
                "barrier_id": self.barrier["id"],
                "id": self.action_plan_individual_stakeholder.id,
            },
        )
        response = self.client.post(
            url,
            follow=False,
            data={"is_organisation": ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES.INDIVIDUAL},
        )
        expected_url = reverse(
            "barriers:action_plan_stakeholders_list",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert "Location" in response
        assert response["Location"] == expected_url

    @skip("WIP")
    def test_add_individual_stakeholder_details(self):
        url = reverse(
            "barriers:action_plan_stakeholders_add_details",
            kwargs={
                "barrier_id": self.barrier["id"],
                "id": self.action_plan_individual_stakeholder.id,
            },
        )
        response = self.client.post(
            url,
            follow=False,
            data={"is_organisation": ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES.INDIVIDUAL},
        )
        expected_url = reverse(
            "barriers:action_plan_stakeholders_list",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert "Location" in response
        assert response["Location"] == expected_url
