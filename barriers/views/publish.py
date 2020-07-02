from django.urls import reverse
from django.views.generic import FormView

from .mixins import APIBarrierFormViewMixin
from barriers.forms.publish import (
    MarkAsReadyForm,
    PublishForm,
    PublicEligibilityForm,
    PublishSummaryForm,
    PublishTitleForm,
)


class PublicBarrier(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/public/overview.html"
    # TODO: Get data from API instead of here
    has_data = True
    is_ready = False

    def get_form_class(self):
        if self.is_ready:
            return PublishForm
        return MarkAsReadyForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["has_data"] = self.has_data
        context_data["is_ready"] = self.is_ready
        context_data["public_barrier"] = self.barrier
        return context_data


class PublicBarrierChanges(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/public/changes.html"
    # TODO: Get data from API instead of here
    has_data = False
    is_ready = False

    def get_form_class(self):
        if self.is_ready:
            return PublishForm
        return MarkAsReadyForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["has_data"] = self.has_data
        context_data["is_ready"] = self.is_ready
        context_data["public_barrier"] = self.barrier
        return context_data


class EditPublishEligibility(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/public/eligibility.html"
    form_class = PublicEligibilityForm

    def get_initial(self):
        initial = {"public_eligibility": self.barrier.public_eligibility}
        if self.barrier.public_eligibility is True:
            initial["allowed_summary"] = self.barrier.public_eligibility_summary
        elif self.barrier.public_eligibility is False:
            initial["not_allowed_summary"] = self.barrier.public_eligibility_summary
        return initial

    def get_success_url(self):
        return reverse(
            "barriers:public_barrier",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )

class EditPublishTitle(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/public/title.html"
    form_class = PublishTitleForm

    def get_success_url(self):
        return reverse(
            "barriers:public_barrier",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class EditPublishSummary(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/public/summary.html"
    form_class = PublishSummaryForm

    def get_success_url(self):
        return reverse(
            "barriers:public_barrier",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
