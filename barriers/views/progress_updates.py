# add and edit views for progress updates
import logging

from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView, View

from barriers.forms.edit import (
    NextStepsItemForm,
    ProgrammeFundProgressUpdateForm,
    Top100ProgressUpdateForm,
)
from barriers.forms.various import ChooseUpdateTypeForm
from barriers.views.mixins import APIBarrierFormViewMixin, BarrierMixin
from utils.api.client import MarketAccessAPIClient
from utils.context_processors import user_scope

logger = logging.getLogger(__name__)


class ChooseProgressUpdateTypeView(BarrierMixin, FormView):
    template_name = "barriers/progress_updates/choose_type.html"
    form_class = ChooseUpdateTypeForm
    success_url_patterns = {
        "top_100_priority": "barriers:add_top_100_progress_update",
        "programme_fund": "barriers:add_programme_fund_progress_update",
    }

    def get_context_data(self, **kwargs):
        kwargs["barrier_id"] = self.kwargs["barrier_id"]
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        success_url_pattern = self.success_url_patterns.get(
            form.cleaned_data["update_type"]
        )
        self.success_url = reverse(
            success_url_pattern, kwargs={"barrier_id": self.kwargs["barrier_id"]}
        )
        return super().form_valid(form)


class BarrierAddTop100ProgressUpdate(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/progress_updates/add_top_100_update.html"
    form_class = Top100ProgressUpdateForm

    def get_initial(self):
        initial = super().get_initial()
        if self.barrier.proposed_estimated_resolution_date:
            proposed_date = self.barrier.proposed_estimated_resolution_date
        else:
            proposed_date = self.barrier.estimated_resolution_date
        if self.barrier.estimated_resolution_date_change_reason:
            proposed_reason = self.barrier.estimated_resolution_date_change_reason
        else:
            proposed_reason = None
        return {
            "estimated_resolution_date": proposed_date,
            "estimated_resolution_date_change_reason": proposed_reason,
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["user"] = user_scope(self.request)["current_user"]
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        return kwargs

    def get_success_url(self):
        success_url = super().get_success_url()
        print("current next steps :", self.barrier.next_steps_items)
        if not self.barrier.next_steps_items:
            return reverse_lazy(
                "barriers:add_next_steps",
                kwargs={"barrier_id": self.kwargs.get("barrier_id")},
            )
        else:
            return reverse_lazy(
                "barriers:list_next_steps",
                kwargs={"barrier_id": self.kwargs.get("barrier_id")},
            )
        # Always route to next steps page
        # if self.form.requested_change:
        #     print(
        #         "there is a change to erd ",
        #         self.kwargs.get("barrier_id"),
        #     )
        #     return reverse_lazy(
        #         "barriers:edit_estimated_resolution_date_confirmation_page",
        #         kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        #     )

        # # if self.barrier.latest_programme_fund_progress_update:
        # else:
        #     #     success_url = f"{success_url}#barrier-top-100-update-tab"
        #     # return success_url
        #     print(
        #         "latest update - redirect to next steps", self.kwargs.get("barrier_id")
        #     )
        #     return reverse_lazy(
        #         "barriers:list_next_steps",
        #         kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        #     )

    def form_valid(self, form):
        self.form = form
        return super().form_valid(form)


class BarrierAddProgrammeFundProgressUpdate(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/progress_updates/add_programme_fund_update.html"
    form_class = ProgrammeFundProgressUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        kwargs["user"] = user_scope(self.request)["current_user"]
        return kwargs

    def get_success_url(self):
        success_url = super().get_success_url()

        if hasattr(self.form, "requested_change") and self.form.requested_change:
            return reverse_lazy(
                "barriers:edit_estimated_resolution_date_confirmation_page",
                kwargs={"barrier_id": self.kwargs.get("barrier_id")},
            )

        if self.barrier.latest_top_100_progress_update:
            success_url = f"{success_url}#barrier-programme-fund-update-tab"
        return success_url

    def form_valid(self, form):
        self.form = form
        return super().form_valid(form)


class BarrierEditProgressUpdate(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/progress_updates/add_top_100_update.html"
    form_class = Top100ProgressUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier_id"] = str(self.kwargs.get("barrier_id"))
        kwargs["progress_update_id"] = str(self.kwargs.get("progress_update_id"))
        kwargs["user"] = user_scope(self.request)["current_user"]
        return kwargs

    def get_success_url(self):
        success_url = super().get_success_url()
        # if self.form.requested_change:
        #     return reverse_lazy(
        #         "barriers:edit_estimated_resolution_date_confirmation_page",
        #         kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        #     )
        if self.barrier.latest_programme_fund_progress_update:
            success_url = f"{success_url}#barrier-top-100-update-tab"
        return success_url

    def form_valid(self, form):
        self.form = form
        return super().form_valid(form)

    def get_initial(self):
        progress_update = next(
            (
                item
                for item in self.barrier.progress_updates
                if item["id"] == str(self.kwargs.get("progress_update_id"))
            ),
            None,
        )
        updates = self.barrier.progress_updates
        progress_update_id = self.kwargs.get("progress_update_id")
        if self.barrier.proposed_estimated_resolution_date:
            proposed_date = self.barrier.proposed_estimated_resolution_date
        else:
            proposed_date = self.barrier.estimated_resolution_date
        if self.barrier.estimated_resolution_date_change_reason:
            proposed_reason = self.barrier.estimated_resolution_date_change_reason
        else:
            proposed_reason = None
        return {
            "status": progress_update["status"],
            "update": progress_update["message"],
            "next_steps": progress_update["next_steps"],
            "estimated_resolution_date": proposed_date,
            "estimated_resolution_date_change_reason": proposed_reason,
        }


class ProgrammeFundEditProgressUpdate(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/progress_updates/edit_programme_fund.html"
    form_class = ProgrammeFundProgressUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        kwargs["progress_update_id"] = str(
            kwargs.get("progress_update_id", self.kwargs.get("progress_update_id"))
        )
        kwargs["user"] = user_scope(self.request)["current_user"]
        return kwargs

    def get_success_url(self):
        success_url = super().get_success_url()
        if self.barrier.latest_top_100_progress_update:
            success_url = f"{success_url}#barrier-programme-fund-update-tab"
        return success_url

    def get_initial(self):
        progress_update = next(
            (
                item
                for item in self.barrier.programme_fund_progress_updates
                if item["id"] == str(self.kwargs.get("progress_update_id"))
            ),
            None,
        )
        updates = self.barrier.programme_fund_progress_updates
        self.progress_update_id = self.kwargs.get("progress_update_id")
        return {
            "milestones_and_deliverables": progress_update[
                "milestones_and_deliverables"
            ],
            "expenditure": progress_update["expenditure"],
        }


class BarrierListProgressUpdate(BarrierMixin, TemplateView):
    template_name = "barriers/progress_updates/list_top_100.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(
            {
                "page": "progress_updates",
                "progress_updates": self.barrier.progress_updates,
            }
        )
        return context_data


class BarrierListNextStepsItems(BarrierMixin, TemplateView):
    template_name = "barriers/progress_updates/list_next_steps_items.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(
            {
                "page": "next_step_items",
                "next_steps_items": self.barrier.next_steps_items,
            }
        )
        return context_data


class BarrierEditNextStepItem(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/progress_updates/add_next_steps_item.html"
    form_class = NextStepsItemForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        form = context_data["form"]
        context_data.update(
            {
                "barrier": self.barrier,
            }
        )
        return context_data

    def get_form_kwargs(self):
        kwargs = super(BarrierEditNextStepItem, self).get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier_id"] = str(self.kwargs.get("barrier_id"))
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        next_step_item = next(
            (
                item
                for item in self.barrier.next_steps_items
                if item["id"] == str(self.kwargs.get("item_id"))
            ),
            None,
        )

        if next_step_item is None:
            return initial
        else:
            return {
                "next_step_owner": next_step_item["next_step_owner"],
                "next_step_item": next_step_item["next_step_item"],
                "status": next_step_item["status"],
                "completion_date": next_step_item["completion_date"],
            }

    def get_success_url(self):

        return reverse_lazy(
            "barriers:list_next_steps",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class ProgrammeFundListProgressUpdate(BarrierMixin, TemplateView):
    template_name = "barriers/progress_updates/list_programme_fund.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(
            {
                "page": "progress_updates",
                "progress_updates": self.barrier.programme_fund_progress_updates,
            }
        )
        return context_data


class BarrierCompleteNextStepItem(View):
    def get(self, request, **kwargs):
        # Get ids from URL arguments
        barrier_id = kwargs["barrier_id"]
        item_id = kwargs["item_id"]
        # Patch next step item in DB to complete
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        client.barriers.patch_next_steps_item(
            barrier=barrier_id,
            id=item_id,
            status="COMPLETED",
        )
        # Redirect back to list of next steps
        return HttpResponseRedirect(f"/barriers/{barrier_id}/list/next_steps_items/")
