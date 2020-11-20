from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from .base import ArchiveAssessmentBase
from ..mixins import BarrierMixin, EconomicAssessmentMixin
from ...forms.assessments.economic import (
    AnalysisDataForm,
    ArchiveEconomicAssessmentForm,
    EconomicAssessmentRatingForm,
    TradeCategoryForm,
)
from users.permissions import APIPermissionMixin
from utils.api.client import MarketAccessAPIClient
from utils.metadata import MetadataMixin


class EconomicAssessmentEditBase(EconomicAssessmentMixin, MetadataMixin, BarrierMixin, FormView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        if self.kwargs.get("assessment_id"):
            kwargs["economic_assessment"] = self.economic_assessment
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:assessment_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class AddEconomicAssessment(APIPermissionMixin, EconomicAssessmentEditBase):
    template_name = "barriers/assessments/economic/add.html"
    permission_required = "add_economicassessment"
    form_class = TradeCategoryForm

    def get_initial(self):
        if self.barrier.trade_category:
            return {"trade_category": self.barrier.trade_category.get("id")}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["barrier"] = self.barrier
        kwargs["trade_categories"] = self.metadata.get_trade_categories()
        return kwargs

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url(form))

    def get_success_url(self, form):
        if form.cleaned_data.get("trade_category") == "GOODS":
            return reverse(
                "barriers:automate_economic_assessment",
                kwargs={"barrier_id": self.kwargs.get("barrier_id")},
            )
        return reverse(
            "barriers:add_economic_assessment_data",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class EditEconomicAssessmentData(APIPermissionMixin, EconomicAssessmentEditBase):
    template_name = "barriers/assessments/economic/edit_data.html"
    permission_required = "change_economicassessment"
    form_class = AnalysisDataForm

    def get_initial(self):
        if self.kwargs.get("assessment_id"):
            return {"analysis_data": self.economic_assessment.analysis_data}

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.kwargs.get("assessment_id"):
            kwargs["economic_assessment"] = self.economic_assessment
        else:
            kwargs["barrier"] = self.barrier
        return kwargs

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url(form))

    def get_success_url(self, form):
        return reverse(
            "barriers:edit_economic_assessment_rating",
            kwargs={
                "barrier_id": self.kwargs.get("barrier_id"),
                "assessment_id": form.economic_assessment.id,
            },
        )


class EditEconomicAssessmentRating(APIPermissionMixin, EconomicAssessmentEditBase):
    template_name = "barriers/assessments/economic/edit_rating.html"
    permission_required = "change_economicassessment"
    form_class = EconomicAssessmentRatingForm

    def get_initial(self):
        initial = {"explanation": self.economic_assessment.explanation}
        if self.economic_assessment.rating:
            initial["rating"] = self.economic_assessment.rating["code"]
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["ratings"] = self.metadata.get_economic_assessment_rating()
        return kwargs


class EconomicAssessmentDetail(EconomicAssessmentMixin, BarrierMixin, TemplateView):
    template_name = "barriers/assessments/economic/detail.html"


class AutomateEconomicAssessment(EconomicAssessmentMixin, BarrierMixin, TemplateView):
    template_name = "barriers/assessments/economic/automate.html"

    def post(self, request, *args, **kwargs):
        client = MarketAccessAPIClient(self.token)
        economic_assessment = client.economic_assessments.create(
            barrier_id=self.barrier.id,
            automate=True,
        )
        return HttpResponseRedirect(self.get_success_url(economic_assessment))

    def get_success_url(self, economic_assessment):
        return reverse(
            "barriers:edit_economic_assessment_rating",
            kwargs={
                "barrier_id": self.kwargs.get("barrier_id"),
                "assessment_id": economic_assessment.id,
            },
        )


class ArchiveEconomicAssessment(APIPermissionMixin, ArchiveAssessmentBase):
    form_class = ArchiveEconomicAssessmentForm
    title = "Archive economic assessment"
    permission_required = "archive_economicassessment"
