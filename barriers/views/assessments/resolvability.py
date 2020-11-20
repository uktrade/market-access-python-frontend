from django.urls import reverse
from django.views.generic import FormView, TemplateView

from .base import ArchiveAssessmentBase
from ..mixins import BarrierMixin, ResolvabilityAssessmentMixin
from ...forms.assessments.resolvability import (
    ResolvabilityAssessmentForm,
    ArchiveResolvabilityAssessmentForm,
)
from users.permissions import APIPermissionMixin
from utils.metadata import MetadataMixin


class ResolvabilityAssessmentEditBase(ResolvabilityAssessmentMixin, MetadataMixin, BarrierMixin, FormView):
    form_class = ResolvabilityAssessmentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["time_to_resolve"] = self.metadata.get_resolvability_assessment_time()
        kwargs["effort_to_resolve"] = self.metadata.get_resolvability_assessment_effort()
        return kwargs

    def get_initial(self):
        if self.kwargs.get("assessment_id"):
            return {
                "time_to_resolve": self.resolvability_assessment.time_to_resolve["id"],
                "effort_to_resolve": self.resolvability_assessment.effort_to_resolve["id"],
                "explanation": self.resolvability_assessment.explanation,
            }

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:assessment_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class AddResolvabilityAssessment(APIPermissionMixin, ResolvabilityAssessmentEditBase):
    template_name = "barriers/assessments/resolvability/add.html"
    permission_required = "add_resolvabilityassessment"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["barrier"] = self.barrier
        return kwargs


class EditResolvabilityAssessment(APIPermissionMixin, ResolvabilityAssessmentEditBase):
    template_name = "barriers/assessments/resolvability/edit.html"
    permission_required = "change_resolvabilityassessment"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["resolvability_assessment"] = self.resolvability_assessment
        return kwargs


class ResolvabilityAssessmentDetail(ResolvabilityAssessmentMixin, BarrierMixin, TemplateView):
    template_name = "barriers/assessments/resolvability/detail.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["assessment"] = self.resolvability_assessment
        return context_data


class ArchiveResolvabilityAssessment(APIPermissionMixin, ArchiveAssessmentBase):
    form_class = ArchiveResolvabilityAssessmentForm
    title = "Archive resolvability assessment"
    permission_required = "archive_resolvabilityassessment"
