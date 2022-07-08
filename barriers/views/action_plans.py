from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from barriers.forms.action_plans import (
    ActionPlanCurrentStatusEditForm,
    ActionPlanMilestoneEditForm,
    ActionPlanMilestoneForm,
    ActionPlanStrategicContextForm,
    ActionPlanTaskEditForm,
    ActionPlanTaskEditOutcomeForm,
    ActionPlanTaskEditProgressForm,
    ActionPlanTaskForm,
    ActionPlanStakeholderTypeForm,
)
from barriers.views.mixins import APIBarrierFormViewMixin, BarrierMixin
from users.mixins import UserSearchMixin
from utils.api.client import MarketAccessAPIClient


class ActionPlanFormSuccessUrlMixin:
    def get_success_url(self):
        return reverse(
            "barriers:action_plan", kwargs={"barrier_id": self.kwargs.get("barrier_id")}
        )


class ActionPlanFormViewMixin(ActionPlanFormSuccessUrlMixin):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        return kwargs


class EditActionPlanCurrentStatusFormView(
    ActionPlanFormViewMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/action_plans/edit_action_plan_current_status.html"
    form_class = ActionPlanCurrentStatusEditForm

    def get_initial(self):
        if self.request.method == "GET":
            return self.action_plan.data


class ActionPlanStakeholderFormViewMixin(ActionPlanFormViewMixin):
    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["stakeholder_id"] = self.kwargs.get("id", None)
        return form_kwargs

    def get_success_url(self):
        return reverse(
            "barriers:action_plan_stakeholders_list",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class CreateActionPlanStakeholderTypeFormView(
    ActionPlanStakeholderFormViewMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/action_plans/stakeholders/edit_type.html"
    form_class = ActionPlanStakeholderTypeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class EditActionPlanStakeholderTypeFormView(
    ActionPlanStakeholderFormViewMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/action_plans/stakeholders/edit_type.html"
    form_class = ActionPlanStakeholderTypeForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SelectActionPlanOwner(
    ActionPlanFormSuccessUrlMixin, BarrierMixin, UserSearchMixin, FormView
):
    template_name = "barriers/action_plans/add_owner.html"
    error_message = "There was an error adding {full_name} as an owner."

    def select_user_api_call(self, user_id):
        self.client.action_plans.edit_action_plan(
            barrier_id=str(self.kwargs.get("barrier_id")), owner=user_id
        )


class AddActionPlanStrategicContext(
    ActionPlanFormViewMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/action_plans/add_strategic_context.html"
    form_class = ActionPlanStrategicContextForm

    def get_initial(self):
        if self.request.method == "GET":
            return self.action_plan.data


class AddActionPlanMilestoneFormView(
    ActionPlanFormViewMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/action_plans/add_milestone.html"
    form_class = ActionPlanMilestoneForm

    def get_initial(self):
        if self.request.method == "GET":
            return self.action_plan.data


class EditActionPlanMilestoneFormView(
    ActionPlanFormViewMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/action_plans/edit_milestone.html"
    form_class = ActionPlanMilestoneEditForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        kwargs["milestone_id"] = self.kwargs.get("id")
        return kwargs

    def get_milestone(self):
        milestones = self.action_plan.milestones
        found = [
            milestone
            for milestone in milestones
            if milestone["id"] == str(self.kwargs.get("id"))
        ]
        return found[0]

    def get_initial(self):
        if self.request.method == "GET":
            return self.get_milestone()


class DeleteActionPlanMilestoneView(BarrierMixin, TemplateView):
    template_name = "barriers/action_plans/delete_milestone_confirm.html"

    def get_milestone(self):
        milestones = self.action_plan.milestones
        found = list(
            filter(
                lambda milestone: milestone["id"] == str(self.kwargs.get("id")),
                milestones,
            )
        )
        return found[0]

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["action_plan"] = self.action_plan
        context_data["milestone"] = self.get_milestone()
        return context_data

    def post(self, request, *args, **kwargs):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        milestone_id = str(self.kwargs.get("id"))
        barrier_id = str(self.kwargs.get("barrier_id"))
        client.action_plans.delete_milestone(barrier_id, milestone_id)
        return HttpResponseRedirect(
            reverse(
                "barriers:action_plan",
                kwargs={"barrier_id": self.kwargs.get("barrier_id")},
            )
        )


class ActionPlanTaskFormViewMixin:
    form_class = ActionPlanTaskForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        kwargs["action_plan_id"] = self.request.GET.get("action_plan")
        kwargs["milestone_id"] = self.request.GET.get("milestone")
        return kwargs

    def get_task(self):
        milestones = self.action_plan.milestones
        for milestone in milestones:
            for task in milestone["tasks"]:
                if task["id"] == str(self.kwargs.get("id")):
                    return {**task, "assigned_to": task["assigned_to_email"]}


class ActionPlanTaskFormView(
    ActionPlanTaskFormViewMixin,
    ActionPlanFormViewMixin,
    APIBarrierFormViewMixin,
    FormView,
):
    template_name = "barriers/action_plans/add_task.html"
    form_class = ActionPlanTaskForm


class AddActionPlanTaskFormView(
    ActionPlanTaskFormViewMixin,
    ActionPlanFormViewMixin,
    APIBarrierFormViewMixin,
    FormView,
):
    template_name = "barriers/action_plans/add_task.html"
    form_class = ActionPlanTaskForm


class EditActionPlanTaskFormView(
    ActionPlanTaskFormViewMixin,
    ActionPlanFormViewMixin,
    APIBarrierFormViewMixin,
    FormView,
):
    template_name = "barriers/action_plans/edit_task.html"
    form_class = ActionPlanTaskEditForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        kwargs["action_plan_id"] = self.request.GET.get("action_plan")
        kwargs["milestone_id"] = self.request.GET.get("milestone")
        kwargs["task_id"] = self.kwargs.get("id")
        return kwargs

    def get_task(self):
        milestones = self.action_plan.milestones
        for milestone in milestones:
            for task in milestone["tasks"]:
                if task["id"] == str(self.kwargs.get("id")):
                    return {**task, "assigned_to": task["assigned_to_email"]}

    def get_initial(self):
        if self.request.method == "GET":
            return self.get_task()


class EditActionPlanTaskOutcomeFormView(
    ActionPlanFormViewMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/action_plans/edit_task_outcome.html"
    form_class = ActionPlanTaskEditOutcomeForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        kwargs["action_plan_id"] = self.request.GET.get("action_plan")
        kwargs["milestone_id"] = self.request.GET.get("milestone")
        kwargs["task_id"] = self.kwargs.get("id")
        return kwargs

    def get_task(self):
        milestones = self.action_plan.milestones
        for milestone in milestones:
            for task in milestone["tasks"]:
                if task["id"] == str(self.kwargs.get("id")):
                    return {**task, "assigned_to": task["assigned_to_email"]}

    def get_initial(self):
        if self.request.method == "GET":
            return self.get_task()


class EditActionPlanTaskProgressFormView(
    ActionPlanTaskFormViewMixin,
    ActionPlanFormViewMixin,
    APIBarrierFormViewMixin,
    FormView,
):
    template_name = "barriers/action_plans/edit_task_progress.html"
    form_class = ActionPlanTaskEditProgressForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        kwargs["action_plan_id"] = self.request.GET.get("action_plan")
        kwargs["milestone_id"] = self.request.GET.get("milestone")
        kwargs["task_id"] = self.kwargs.get("id")
        return kwargs

    def get_initial(self):
        if self.request.method == "GET":
            return self.get_task()


class DeleteActionPlanTaskView(ActionPlanTaskFormViewMixin, BarrierMixin, TemplateView):
    template_name = "barriers/action_plans/delete_task_confirm.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["action_plan"] = self.action_plan
        context_data["task"] = self.get_task()
        return context_data

    def post(self, request, *args, **kwargs):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        task_id = str(self.kwargs.get("id"))
        barrier_id = str(self.kwargs.get("barrier_id"))
        client.action_plans.delete_task(barrier_id, task_id)
        return HttpResponseRedirect(
            reverse(
                "barriers:action_plan",
                kwargs={"barrier_id": self.kwargs.get("barrier_id")},
            )
        )


class ActionPlanTemplateView(BarrierMixin, TemplateView):
    template_name = "barriers/action_plans/detail.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["action_plan"] = self.action_plan
        return context_data


class ActionPlanStakeholdersListView(BarrierMixin, TemplateView):
    template_name = "barriers/action_plans/stakeholders/list.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["action_plan"] = self.action_plan
        return context_data


class AddActionPlanStakeholderFormView(
    ActionPlanTaskFormViewMixin,
    ActionPlanFormViewMixin,
    APIBarrierFormViewMixin,
    FormView,
):
    template_name = "barriers/action_plans/add_task.html"
    form_class = ActionPlanTaskForm
