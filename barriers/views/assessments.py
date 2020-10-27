from django.urls import reverse
from django.views.generic import FormView, RedirectView, TemplateView

from ..forms.assessments import (
    AssessmentDocumentForm,
    CommercialValueForm,
    EconomicAssessmentForm,
    EconomyValueForm,
    ExportValueForm,
    MarketSizeForm,
    ResolvabilityAssessmentForm,
    ArchiveResolvabilityAssessmentForm,
)
from .documents import AddDocumentAjaxView, DeleteDocumentAjaxView
from .mixins import AssessmentMixin, BarrierMixin, SessionDocumentMixin
from utils.metadata import MetadataMixin


class AssessmentSessionDocumentMixin(SessionDocumentMixin):
    def get_session_key(self):
        barrier_id = self.kwargs.get("barrier_id")
        return f"barrier:{barrier_id}:assessment_documents"


class AssessmentDetail(AssessmentMixin, BarrierMixin, TemplateView):
    template_name = "barriers/assessments/detail.html"


class EconomicAssessment(
    AssessmentSessionDocumentMixin, AssessmentMixin, BarrierMixin, FormView,
):
    template_name = "barriers/assessments/economic.html"
    form_class = EconomicAssessmentForm

    def get(self, request, *args, **kwargs):
        if self.barrier.has_assessment:
            session_key = self.get_session_key()
            if session_key not in self.request.session:
                self.set_session_documents(self.assessment.documents)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["documents"] = self.get_session_documents()
        return context_data

    def get_initial(self):
        if self.request.method == "GET" and self.barrier.has_assessment:
            initial = {"description": self.assessment.explanation}
            if self.assessment.impact:
                initial["impact"] = self.assessment.impact.get("code")
            return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["barrier"] = self.barrier
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs

    def form_valid(self, form):
        form.save()
        self.delete_session_documents()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:assessment_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class NewEconomicAssessment(RedirectView):
    """
    Clears the session and redirects to the economic assessment page
    """

    def get(self, request, *args, **kwargs):
        try:
            del self.request.session["assessment_documents"]
        except KeyError:
            pass
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            "barriers:economic_assessment",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class AddAssessmentDocument(
    AssessmentSessionDocumentMixin, AddDocumentAjaxView,
):
    form_class = AssessmentDocumentForm

    def get_delete_url(self, document):
        return reverse(
            "barriers:delete_assessment_document",
            kwargs={
                "barrier_id": self.kwargs.get("barrier_id"),
                "document_id": document["id"],
            },
        )


class DeleteAssessmentDocument(
    AssessmentSessionDocumentMixin, DeleteDocumentAjaxView,
):
    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            "barriers:economic_assessment",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class CancelAssessmentDocument(AssessmentSessionDocumentMixin, RedirectView):
    """
    Clears the session and redirects to the barrier detail page
    """

    def get(self, request, *args, **kwargs):
        self.delete_session_documents()
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            "barriers:assessment_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class AssessmentValueView(AssessmentMixin, BarrierMixin, FormView):
    """
    Base class to be used by views which update one field of an Assessment
    """

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["barrier"] = self.barrier
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:assessment_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class EconomyValueAssessment(AssessmentValueView, FormView):
    template_name = "barriers/assessments/economy_value.html"
    form_class = EconomyValueForm

    def get_initial(self):
        if self.assessment:
            return {"value": self.assessment.value_to_economy}


class MarketSizeAssessment(AssessmentValueView, FormView):
    template_name = "barriers/assessments/market_size.html"
    form_class = MarketSizeForm

    def get_initial(self):
        if self.assessment:
            return {"value": self.assessment.import_market_size}


class CommercialValueAssessment(AssessmentValueView):
    template_name = "barriers/assessments/commercial_value.html"
    form_class = CommercialValueForm

    def get_initial(self):
        if self.assessment:
            return {
                "value": self.assessment.commercial_value,
                "value_explanation": self.assessment.commercial_value_explanation or ""
            }


class ExportValueAssessment(AssessmentValueView):
    template_name = "barriers/assessments/export_value.html"
    form_class = ExportValueForm

    def get_initial(self):
        if self.assessment:
            return {"value": self.assessment.export_value}


class AddResolvabilityAssessment(MetadataMixin, BarrierMixin, FormView):
    template_name = "barriers/assessments/resolvability/add.html"
    form_class = ResolvabilityAssessmentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["barrier"] = self.barrier
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["metadata"] = self.metadata
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:assessment_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class EditResolvabilityAssessment(AssessmentMixin, BarrierMixin, TemplateView):
    template_name = "barriers/assessments/resolvability/edit.html"
    form_class = ResolvabilityAssessmentForm


class ArchiveResolvabilityAssessment(BarrierMixin, FormView):
    template_name = "barriers/assessments/resolvability/archive.html"
    form_class = ArchiveResolvabilityAssessmentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["id"] = self.kwargs["assessment_id"]
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:assessment_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class ResolvabilityAssessmentDetail(BarrierMixin, TemplateView):
    template_name = "barriers/assessments/resolvability/detail.html"

    def get_resolvability_assessment(self):
        for assessment in self.barrier.resolvability_assessments:
            if assessment.id == str(self.kwargs.get("assessment_id")):
                return assessment

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["assessment"] = self.get_resolvability_assessment()
        return context_data
