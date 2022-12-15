from django.urls import reverse
from django.views.generic import FormView, TemplateView

from users.permissions import APIPermissionMixin
from utils.metadata import MetadataMixin

from ...forms.assessments.economic_impact import (
    ArchiveEconomicImpactAssessmentForm,
    EconomicImpactAssessmentForm,
)
from ..mixins import BarrierMixin, EconomicImpactAssessmentMixin
from .base import ArchiveAssessmentBase


class EconomicImpactAssessmentEditBase(MetadataMixin, BarrierMixin, FormView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["impacts"] = self.metadata.get_economic_assessment_impact()
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:assessment_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class AddEconomicImpactAssessment(APIPermissionMixin, EconomicImpactAssessmentEditBase):
    template_name = "barriers/assessments/economic_impact/add.html"
    permission_required = "add_economicimpactassessment"
    form_class = EconomicImpactAssessmentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["economic_assessment"] = self.barrier.current_economic_assessment
        kwargs["barrier"] = self.barrier
        return kwargs


class EconomicImpactAssessmentDetail(
    EconomicImpactAssessmentMixin, BarrierMixin, TemplateView
):
    template_name = "barriers/assessments/economic_impact/detail.html"


class ArchiveEconomicImpactAssessment(APIPermissionMixin, ArchiveAssessmentBase):
    form_class = ArchiveEconomicImpactAssessmentForm
    title = "Archive valuation assessment"
    permission_required = "archive_economicimpactassessment"
