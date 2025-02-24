from django.urls import reverse_lazy
from django.views.generic import FormView

from barriers.forms.estimated_resolution_date import (
    AddEstimatedResolutionDateForm,
    EditEstimatedResolutionDateForm,
    DeleteEstimatedResolutionDateForm,
    ReviewEstimatedResolutionDateForm,
    RejectEstimatedResolutionDateForm,
    ApproveEstimatedResolutionDateForm,
    ConfirmationEstimatedResolutionDateForm
)
from barriers.views.mixins import APIBarrierFormViewMixin
from utils.api.client import MarketAccessAPIClient


class EstimatedResolutionDateFormMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["barrier_id"] = self.kwargs.get("barrier_id")
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        return kwargs


class AddEstimatedResolutionDateFormView(EstimatedResolutionDateFormMixin, APIBarrierFormViewMixin, FormView):
    template_name = "barriers/estimated_resolution_date/forms/add.html"
    form_class = AddEstimatedResolutionDateForm

    def get_success_url(self):
        return reverse_lazy(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class EditEstimatedResolutionDateFormView(EstimatedResolutionDateFormMixin, APIBarrierFormViewMixin, FormView):
    template_name = "barriers/estimated_resolution_date/forms/edit.html"
    form_class = EditEstimatedResolutionDateForm

    def get_success_url(self):
        return reverse_lazy(
            "barriers:confirmation_estimated_resolution_date",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )

    def get_initial(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        erd_request = client.erd_request.get(barrier_id=self.kwargs.get("barrier_id"))
        if erd_request:
            proposed_date = erd_request.estimated_resolution_date
            proposed_reason = erd_request.reason
        else:
            proposed_date = erd_request
            proposed_reason = None

        return {
            "estimated_resolution_date": proposed_date,
            "estimated_resolution_date_change_reason": proposed_reason,
        }


class DeleteEstimatedResolutionDateFormView(EstimatedResolutionDateFormMixin, APIBarrierFormViewMixin, FormView):
    template_name = "barriers/estimated_resolution_date/forms/delete.html"
    form_class = DeleteEstimatedResolutionDateForm

    def get_success_url(self):
        return reverse_lazy(
            "barriers:confirmation_estimated_resolution_date",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class ReviewEstimatedResolutionDateFormView(EstimatedResolutionDateFormMixin, APIBarrierFormViewMixin, FormView):
    template_name = "barriers/estimated_resolution_date/forms/review.html"
    form_class = ReviewEstimatedResolutionDateForm

    def get_success_url(self):
        return reverse_lazy(
            "barriers:approve_estimated_resolution_date",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class ApproveEstimatedResolutionDateFormView(EstimatedResolutionDateFormMixin, APIBarrierFormViewMixin, FormView):
    template_name = "barriers/estimated_resolution_date/forms/approve.html"
    form_class = ApproveEstimatedResolutionDateForm

    def get_success_url(self):
        return reverse_lazy(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class RejectEstimatedResolutionDateFormView(EstimatedResolutionDateFormMixin, APIBarrierFormViewMixin, FormView):
    template_name = "barriers/estimated_resolution_date/forms/reject.html"
    form_class = RejectEstimatedResolutionDateForm

    def get_success_url(self):
        return reverse_lazy(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class ConfirmationEstimatedResolutionDateFormView(EstimatedResolutionDateFormMixin, APIBarrierFormViewMixin, FormView):
    template_name = "barriers/estimated_resolution_date/forms/confirmation.html"
    form_class = ConfirmationEstimatedResolutionDateForm

    def get_success_url(self):
        return reverse_lazy(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
