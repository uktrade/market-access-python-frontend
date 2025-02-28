from django.urls import reverse_lazy
from django.views.generic import FormView

from barriers.forms.estimated_resolution_date import (
    AddEstimatedResolutionDateForm,
    ApproveEstimatedResolutionDateForm,
    ConfirmationEstimatedResolutionDateForm,
    DeleteEstimatedResolutionDateForm,
    EditEstimatedResolutionDateForm,
    RejectEstimatedResolutionDateForm,
    ReviewEstimatedResolutionDateForm,
)
from barriers.views.mixins import AdminMixin, APIBarrierFormViewMixin


class AddEstimatedResolutionDateFormView(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/estimated_resolution_date/forms/add.html"
    form_class = AddEstimatedResolutionDateForm

    def get_success_url(self):
        return reverse_lazy(
            "barriers:confirmation_estimated_resolution_date",
            kwargs={"barrier_id": self.get_object().id},
        )


class EditEstimatedResolutionDateFormView(
    AdminMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/estimated_resolution_date/forms/edit.html"
    form_class = EditEstimatedResolutionDateForm

    def get_success_url(self):
        return reverse_lazy(
            "barriers:confirmation_estimated_resolution_date",
            kwargs={"barrier_id": self.get_object().id},
        )


class DeleteEstimatedResolutionDateFormView(
    AdminMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/estimated_resolution_date/forms/delete.html"
    form_class = DeleteEstimatedResolutionDateForm

    def get_success_url(self):
        return reverse_lazy(
            "barriers:confirmation_estimated_resolution_date",
            kwargs={"barrier_id": self.get_object().id},
        )


class ReviewEstimatedResolutionDateFormView(
    AdminMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/estimated_resolution_date/forms/review.html"
    form_class = ReviewEstimatedResolutionDateForm

    def get_success_url(self):
        return reverse_lazy(
            "barriers:approve_estimated_resolution_date",
            kwargs={"barrier_id": self.get_object().id},
        )


class ApproveEstimatedResolutionDateFormView(
    AdminMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/estimated_resolution_date/forms/approve.html"
    form_class = ApproveEstimatedResolutionDateForm

    def get_success_url(self):
        return reverse_lazy(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.get_object().id},
        )


class RejectEstimatedResolutionDateFormView(
    AdminMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/estimated_resolution_date/forms/reject.html"
    form_class = RejectEstimatedResolutionDateForm

    def get_success_url(self):
        return reverse_lazy(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.get_object().id},
        )


class ConfirmationEstimatedResolutionDateFormView(
    AdminMixin, APIBarrierFormViewMixin, FormView
):
    template_name = "barriers/estimated_resolution_date/forms/confirmation.html"
    form_class = ConfirmationEstimatedResolutionDateForm

    def get_success_url(self):
        return reverse_lazy(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.get_object().id},
        )
