from django.urls import reverse
from django.views.generic import FormView, TemplateView

from .base import ArchiveAssessmentBase
from ..mixins import BarrierMixin, StrategicAssessmentMixin
from ...forms.assessments.strategic import (
    StrategicAssessmentForm,
    ArchiveStrategicAssessmentForm,
)
from users.permissions import APIPermissionMixin
from utils.metadata import MetadataMixin


class StrategicAssessmentEditBase(StrategicAssessmentMixin, MetadataMixin, BarrierMixin, FormView):
    form_class = StrategicAssessmentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["scale"] = self.metadata.get_strategic_assessment_scale()
        return kwargs

    def get_initial(self):
        if self.kwargs.get("assessment_id"):
            return {
                "scale": self.strategic_assessment.scale["id"],
                "hmg_strategy": self.strategic_assessment.hmg_strategy,
                "government_policy": self.strategic_assessment.government_policy,
                "trading_relations": self.strategic_assessment.trading_relations,
                "uk_interest_and_security": self.strategic_assessment.uk_interest_and_security,
                "uk_grants": self.strategic_assessment.uk_grants,
                "competition": self.strategic_assessment.competition,
                "additional_information": self.strategic_assessment.additional_information,
            }

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:assessment_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class AddStrategicAssessment(APIPermissionMixin, StrategicAssessmentEditBase):
    template_name = "barriers/assessments/strategic/add.html"
    permission_required = "add_strategicassessment"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["barrier"] = self.barrier
        return kwargs


class EditStrategicAssessment(APIPermissionMixin, StrategicAssessmentEditBase):
    template_name = "barriers/assessments/strategic/edit.html"
    permission_required = "change_strategicassessment"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["strategic_assessment"] = self.strategic_assessment
        return kwargs


class StrategicAssessmentDetail(StrategicAssessmentMixin, BarrierMixin, TemplateView):
    template_name = "barriers/assessments/strategic/detail.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["assessment"] = self.strategic_assessment
        return context_data


class ArchiveStrategicAssessment(APIPermissionMixin, ArchiveAssessmentBase):
    form_class = ArchiveStrategicAssessmentForm
    title = "Archive strategic assessment"
    permission_required = "archive_strategicassessment"
