from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from .mixins import APIBarrierFormViewMixin, BarrierMixin
from barriers.forms.publish import (
    PublicEligibilityForm,
    PublishSummaryForm,
    PublishTitleForm,
)

from utils.api.client import MarketAccessAPIClient


class PublicBarrierMixin:
    _public_barrier = None

    @property
    def public_barrier(self):
        if not self._public_barrier:
            self._public_barrier = self.get_public_barrier()
        return self._public_barrier

    def get_public_barrier(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        barrier_id = self.kwargs.get("barrier_id")
        return client.public_barriers.get(id=barrier_id)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["public_barrier"] = self.public_barrier
        return context_data


class PublicBarrier(PublicBarrierMixin, BarrierMixin, TemplateView):
    template_name = "barriers/public/overview.html"

    def post(self, request, *args, **kwargs):
        action = self.request.POST.get("action")
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        barrier_id = self.kwargs.get("barrier_id")

        if action:
            if action == "mark-as-ready":
                client.public_barriers.mark_as_ready(id=barrier_id)
            elif action == "publish":
                client.public_barriers.publish(id=barrier_id)
            return HttpResponseRedirect(self.get_success_url())
        return self.render_to_response(self.get_context_data())

    def get_success_url(self):
        return reverse(
            "barriers:public_barrier",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class PublicBarrierChanges(APIBarrierFormViewMixin, PublicBarrierMixin, FormView):
    template_name = "barriers/public/changes.html"

    def get_form_class(self):
        if self.is_ready:
            return PublishForm
        return MarkAsReadyForm


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


class EditPublishTitle(APIBarrierFormViewMixin, PublicBarrierMixin, FormView):
    template_name = "barriers/public/title.html"
    form_class = PublishTitleForm

    def get_initial(self):
        return {"title": self.public_barrier.title["public"]}

    def get_success_url(self):
        return reverse(
            "barriers:public_barrier",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class EditPublishSummary(APIBarrierFormViewMixin, PublicBarrierMixin, FormView):
    template_name = "barriers/public/summary.html"
    form_class = PublishSummaryForm

    def get_initial(self):
        return {"summary": self.public_barrier.summary["public"]}

    def get_success_url(self):
        return reverse(
            "barriers:public_barrier",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
