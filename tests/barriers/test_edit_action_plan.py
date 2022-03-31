from django.test import RequestFactory
from django.urls import reverse

from barriers.views.action_plans import SelectActionPlanOwner
from core.tests import MarketAccessTestCase


class ActionPlanTestCase(MarketAccessTestCase):
    def test_select_action_plan_owner_form_kwargs_exclude_barrier_id(self):
        request_factory = RequestFactory()
        request = request_factory.get(
            reverse(
                "barriers:action_plan_edit_owner",
                kwargs={"barrier_id": self.barrier["id"]},
            )
        )
        view = SelectActionPlanOwner()
        view.setup(request, barrier_id=self.barrier["id"])
        form_kwargs = view.get_form_kwargs()
        assert "barrier_id" not in form_kwargs

    def test_select_action_plan_owner_success_url_is_action_plan_url(self):
        request_factory = RequestFactory()
        request = request_factory.get(
            reverse(
                "barriers:action_plan_edit_owner",
                kwargs={"barrier_id": self.barrier["id"]},
            )
        )
        view = SelectActionPlanOwner()
        view.setup(request, barrier_id=self.barrier["id"])
        success_url = view.get_success_url()
        expected_success_url = reverse(
            "barriers:action_plan",
            kwargs={"barrier_id": self.barrier["id"]},
        )
        assert success_url == expected_success_url
