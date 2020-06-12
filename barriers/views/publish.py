from django.urls import reverse
from django.views.generic import FormView, RedirectView, TemplateView

from .mixins import APIBarrierFormViewMixin, BarrierMixin
from barriers.forms.publish import (
    MarkAsReadyForm,
    PublishEligibilityForm,
    PublishForm,
    PublishSummaryForm,
    PublishTitleForm,
)

from utils.metadata import get_metadata


class PublishBarrier(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/publish/publish.html"
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
        return context_data


class EditPublishEligibility(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/publish/eligibility.html"
    form_class = PublishEligibilityForm

    def get_initial(self):
        return {
            "is_publishable": False,
        }


class EditPublishTitle(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/publish/title.html"
    form_class = PublishTitleForm

    def get_success_url(self):
        return reverse(
            "barriers:publish_barrier",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class EditPublishSummary(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/publish/summary.html"
    form_class = PublishSummaryForm

    def get_success_url(self):
        return reverse(
            "barriers:publish_barrier",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
