from http import HTTPStatus

from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, TemplateView
from formtools.wizard.views import SessionWizardView

from barriers.constants import ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES
from barriers.forms.action_plans import (
    ActionPlanCurrentStatusEditForm,
    ActionPlanIndividualStakeholderDetailsForm,
    ActionPlanMilestoneForm,
    ActionPlanOrganisationStakeholderDetailsForm,
    ActionPlanRisksAndMitigationForm,
    ActionPlanRisksAndMitigationIntroForm,
    ActionPlanStakeholderTypeForm,
    ActionPlanStrategicContextForm,
    ActionPlanTaskDateChangeReasonForm,
    ActionPlanTaskEditOutcomeForm,
    ActionPlanTaskEditProgressForm,
    ActionPlanTaskForm,
)
from barriers.views.mixins import APIBarrierFormViewMixin, BarrierMixin
from users.mixins import UserSearchMixin
from utils.api.client import MarketAccessAPIClient
from utils.exceptions import APIHttpException


class ActionPlanFormSuccessUrlMixin:
    def get_success_url(self):
        return reverse(
            "barriers:action_plan", kwargs={"barrier_id": self.kwargs.get("barrier_id")}
        )


class ActionPlanFormViewMixin(ActionPlanFormSuccessUrlMixin):
    _action_plan = None

    @property
    def action_plan(self):
        if not self._action_plan:
            self._action_plan = self.get_action_plan()
        return self._action_plan

    def get_action_plan(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        barrier_id = self.kwargs.get("barrier_id")
        try:
            return client.action_plans.get_barrier_action_plan(barrier_id=barrier_id)
        except APIHttpException as e:
            if e.status_code == HTTPStatus.NOT_FOUND:
                raise Http404()
            raise

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs()
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        kwargs["action_plan"] = self.action_plan
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["action_plan"] = self.action_plan
        context["barrier_id"] = self.action_plan.barrier
        context["stakeholder"] = self.object
        return context


class EditActionPlanCurrentStatusFormView(
    ActionPlanFormViewMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/action_plans/edit_action_plan_current_status.html"
    form_class = ActionPlanCurrentStatusEditForm

    def get_initial(self):
        if self.request.method == "GET":
            return self.action_plan.data


class ActionPlanStakeholderFormViewMixin(ActionPlanFormViewMixin):
    def get_object(self):
        stakeholder_id = self.kwargs.get("id")
        stakeholder = self.action_plan.get_stakeholder(stakeholder_id)
        return stakeholder

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["stakeholder_id"] = self.kwargs.get("id", None)
        return form_kwargs

    def get_success_url(self):
        if hasattr(self, "saved_object"):
            self.kwargs["id"] = self.saved_object.id
        return reverse(
            "barriers:action_plan_stakeholders_edit",
            kwargs={
                "id": self.kwargs.get("id"),
                "barrier_id": self.kwargs.get("barrier_id"),
            },
        )


class CreateActionPlanStakeholderTypeFormView(
    ActionPlanFormViewMixin,
    APIBarrierFormViewMixin,
    FormView,
):
    template_name = "barriers/action_plans/stakeholders/edit_type.html"
    form_class = ActionPlanStakeholderTypeForm

    def form_valid(self, form):
        # allow access to form data in get_success_url
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        is_organisation = self.form.cleaned_data["is_organisation"]
        if is_organisation == ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES.ORGANISATION:
            return reverse(
                "barriers:action_plan_stakeholders_new_organisation",
                kwargs={"barrier_id": self.kwargs.get("barrier_id")},
            )
        if is_organisation == ACTION_PLAN_STAKEHOLDER_TYPE_CHOICES.INDIVIDUAL:
            return reverse(
                "barriers:action_plan_stakeholders_new_individual",
                kwargs={"barrier_id": self.kwargs.get("barrier_id")},
            )


class EditActionPlanStakeholderDetailsFormView(
    ActionPlanStakeholderFormViewMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/action_plans/stakeholders/edit_details.html"

    def get_form_class(self):
        if self.object.is_organisation:
            return ActionPlanOrganisationStakeholderDetailsForm
        else:
            return ActionPlanIndividualStakeholderDetailsForm

    def get_initial(self):
        initial = super().get_initial()
        initial["name"] = self.object.name
        initial["status"] = self.object.status
        if not self.object.is_organisation:
            initial["organisation"] = self.object.organisation
            initial["job_title"] = self.object.job_title
        return initial

    def get_success_url(self):
        return reverse(
            "barriers:action_plan_stakeholders_list",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class CreateActionPlanStakeholderIndividualFormView(
    ActionPlanStakeholderFormViewMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/action_plans/stakeholders/edit_details.html"
    form_class = ActionPlanIndividualStakeholderDetailsForm

    def get_success_url(self):
        return reverse(
            "barriers:action_plan_stakeholders_list",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class CreateActionPlanStakeholderOrganisationFormView(
    ActionPlanStakeholderFormViewMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/action_plans/stakeholders/edit_details.html"
    form_class = ActionPlanOrganisationStakeholderDetailsForm

    def get_success_url(self):
        return reverse(
            "barriers:action_plan_stakeholders_list",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class SelectActionPlanOwner(
    ActionPlanFormSuccessUrlMixin, BarrierMixin, UserSearchMixin, FormView
):
    template_name = "barriers/action_plans/add_owner.html"
    error_message = "There was an error adding {full_name} as an owner."

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data["cancel_url"] = reverse(
            "barriers:action_plan", kwargs={"barrier_id": self.kwargs.get("barrier_id")}
        )
        return context_data

    def select_user_api_call(self, user_id):
        self.client.action_plans.edit_action_plan(
            barrier_id=str(self.kwargs.get("barrier_id")), owner=user_id
        )


class EditActionPlanOwner(
    ActionPlanFormViewMixin, APIBarrierFormViewMixin, TemplateView
):
    template_name = "barriers/action_plans/edit_owner.html"


class RemoveActionPlanOwner(ActionPlanFormViewMixin, APIBarrierFormViewMixin, View):
    def get(self, request, *args, **kwargs):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        client.action_plans.edit_action_plan(
            barrier_id=str(self.kwargs.get("barrier_id")), owner=None
        )
        return HttpResponseRedirect(
            reverse(
                "barriers:action_plan",
                kwargs={"barrier_id": self.kwargs.get("barrier_id")},
            )
        )


class AddActionPlanStrategicContext(
    ActionPlanFormViewMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/action_plans/add_strategic_context.html"
    form_class = ActionPlanStrategicContextForm

    def get_initial(self):
        if self.request.method == "GET":
            return self.action_plan.data


class ActionPlanMilestoneFormView(
    ActionPlanFormViewMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/action_plans/milestone_detail.html"
    form_class = ActionPlanMilestoneForm
    title = "Add objective"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        if "id" in self.kwargs:
            self.title = "Edit objective"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["milestone_id"] = self.kwargs.get("id", None)
        return kwargs

    def get_milestone(self):
        milestone = self.action_plan.get_milestone(self.kwargs.get("id"))
        return milestone

    def get_initial(self):
        milestone = self.get_milestone()
        if milestone:
            return {**milestone.data}
        return {}


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


class ActionPlanTaskFormView(
    ActionPlanFormViewMixin,
    APIBarrierFormViewMixin,
    FormView,
):
    template_name = "barriers/action_plans/edit_milestone_task.html"
    form_class = ActionPlanTaskForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # for some unexplained reason from 2019, APIFormMixin skips get_initial() for POST and PUT
        if "initial" not in kwargs:
            kwargs["initial"] = self.get_initial()
        kwargs["task_id"] = self.kwargs.get("id")
        return kwargs

    def get_task(self):
        milestone = self.action_plan.get_milestone(self.kwargs.get("milestone_id"))
        task = milestone.get_task(self.kwargs.get("id"))
        return task

    def get_initial(self):
        initial = {}
        task = self.get_task()
        if task:
            initial.update(task.data)
            initial["assigned_to"] = task.assigned_to_email
        if "action_type" in initial and initial["action_type"]:
            action_type = initial["action_type"]
            initial[f"action_type_category_{action_type}"] = initial[
                "action_type_category"
            ]
        return initial

    def form_valid(self, form):
        """
        If the form is valid but the completion date has changed, we need to re-render
        but with a different template and extended form that asks for a reason for that change.

        The "id" is only in self.kwargs if we're changing an existing instance;
        "completion_date" will also be in changed_data for the case of creating a new one,
        so we need both checks.
        """
        if all(
            [
                "id"
                in self.kwargs,  # must be an existing instance, not creating a new one
                "completion_date"
                in form.changed_data,  # must be an update to completion_date
                self.form_class
                == ActionPlanTaskForm,  # must be using a form that doesn't ask for a reason
            ]
        ):
            response_kwargs = {}
            response_kwargs.setdefault("content_type", self.content_type)
            # Need to replace the form with an unbound form that asks for a reason
            # All other fields will be turned into hidden fields
            form_kwargs = self.get_form_kwargs()
            form_kwargs["initial"] = form.cleaned_data
            # Those subforms will be the death of me
            if hasattr(form.fields["status"].subforms["IN_PROGRESS"], "cleaned_data"):
                form_kwargs["initial"]["progress"] = (
                    form.fields["status"]
                    .subforms["IN_PROGRESS"]
                    .cleaned_data["progress"]
                )
            else:
                form_kwargs["initial"]["progress"] = form.data.get("progress", "")
            if hasattr(form.fields["status"].subforms["COMPLETED"], "cleaned_data"):
                form_kwargs["initial"]["outcome"] = (
                    form.fields["status"].subforms["COMPLETED"].cleaned_data["outcome"]
                )
            else:
                form_kwargs["initial"]["outcome"] = form.data.get("outcome", "")
            # Need to get rid of files and data to ensure form is not bound
            form_kwargs.pop("files")
            form_kwargs.pop("data")
            unbound_form = ActionPlanTaskDateChangeReasonForm(**form_kwargs)

            context = self.get_context_data()
            context["form"] = unbound_form
            context["form_action"] = reverse(
                "barriers:action_plan_completion_date_change",
                kwargs=self.kwargs,
            )
            return self.response_class(
                request=self.request,
                template="barriers/action_plans/milestone_task_completion_date_reason.html",
                context=context,
                using=self.template_engine,
                **response_kwargs,
            )
        return super().form_valid(form)


class ActionPlanTaskCompletionDateChangeFormView(ActionPlanTaskFormView):
    form_class = ActionPlanTaskDateChangeReasonForm
    template_name = "barriers/action_plans/milestone_task_completion_date_reason.html"


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
    # ActionPlanTaskFormViewMixin,
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


class DeleteActionPlanTaskView(
    # ActionPlanTaskFormViewMixin,
    BarrierMixin,
    TemplateView,
):
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
    ActionPlanFormViewMixin,
    APIBarrierFormViewMixin,
    FormView,
):
    template_name = "barriers/action_plans/edit_milestone_task.html"
    form_class = ActionPlanTaskForm


class ActionPlanRisksAndMitigationView(
    ActionPlanFormViewMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/action_plans/add_risks_and_mitigation.html"
    form_class = ActionPlanRisksAndMitigationForm

    def get_initial(self):
        if self.request.method == "GET":
            return self.action_plan.data


def risks_and_mitigation_detail_form_condition(wizard):
    step0_cleaned_data = wizard.get_cleaned_data_for_step("0")
    if step0_cleaned_data:
        return step0_cleaned_data.get("has_risks") == "YES"
    return False


class ActionPlanRisksAndMitigationWizardView(
    ActionPlanFormViewMixin, APIBarrierFormViewMixin, SessionWizardView
):
    template_name = "barriers/action_plans/add_risks_and_mitigation.html"
    form_list = [
        ActionPlanRisksAndMitigationIntroForm,
        ActionPlanRisksAndMitigationForm,
    ]
    condition_dict = {"1": risks_and_mitigation_detail_form_condition}

    def get_form_initial(self, step):
        return self.action_plan.data

    def done(self, form_list, **kwargs):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))

        cleaned_data = self.get_all_cleaned_data()

        client.action_plans.edit_action_plan(
            barrier_id=self.barrier.id,
            has_risks=cleaned_data.get("has_risks"),
            potential_unwanted_outcomes=cleaned_data.get("potential_unwanted_outcomes"),
            potential_risks=cleaned_data.get("potential_risks"),
            risk_level=cleaned_data.get("risk_level"),
            risk_mitigation_measures=cleaned_data.get("risk_mitigation_measures"),
        )

        return HttpResponseRedirect(
            reverse(
                "barriers:action_plan",
                kwargs={"barrier_id": self.kwargs.get("barrier_id")},
            )
        )
