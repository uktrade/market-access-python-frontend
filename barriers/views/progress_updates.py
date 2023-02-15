# add and edit views for progress updates
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView

from barriers.forms.edit import (
    ProgrammeFundProgressUpdateForm,
    Top100ProgressUpdateForm,
)
from barriers.forms.various import ChooseUpdateTypeForm
from barriers.views.mixins import APIBarrierFormViewMixin, BarrierMixin
from utils.context_processors import user_scope


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
        estimated_resolution_date = self.barrier.estimated_resolution_date
        if estimated_resolution_date:
            initial["estimated_resolution_date"] = estimated_resolution_date
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["user"] = user_scope(self.request)["current_user"]
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        return kwargs

    def get_success_url(self):
        success_url = super().get_success_url()
        if self.form.requested_change:
            return reverse_lazy(
                "barriers:edit_estimated_resolution_date_confirmation_page",
                kwargs={"barrier_id": self.kwargs.get("barrier_id")},
            )
        if self.barrier.latest_programme_fund_progress_update:
            success_url = f"{success_url}#barrier-top-100-update-tab"
        return success_url

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
        return kwargs

    def get_success_url(self):
        success_url = super().get_success_url()

        if self.form.requested_change:
            return reverse_lazy(
                "barriers:edit_estimated_resolution_date_confirmation_page",
                kwargs={"barrier_id": self.kwargs.get("barrier_id")},
            )

        if self.barrier.latest_top_100_progress_update:
            success_url = f"{success_url}#barrier-programme-fund-update-tab"
        return success_url


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
        if self.form.requested_change:
            return reverse_lazy(
                "barriers:edit_estimated_resolution_date_confirmation_page",
                kwargs={"barrier_id": self.kwargs.get("barrier_id")},
            )
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
        return {
            "status": progress_update["status"],
            "update": progress_update["message"],
            "next_steps": progress_update["next_steps"],
        }


class ProgrammeFundEditProgressUpdate(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/progress_updates/edit_programme_fund.html"
    form_class = ProgrammeFundProgressUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier_id"] = str(self.kwargs.get("barrier_id"))
        kwargs["programme_fund_update_id"] = str(
            kwargs.pop("progress_update_id", self.kwargs.get("progress_update_id"))
        )
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
        progress_update_id = self.kwargs.get("progress_update_id")
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
