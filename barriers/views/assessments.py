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
    StrategicAssessmentForm,
    ArchiveResolvabilityAssessmentForm,
    ArchiveStrategicAssessmentForm,
)
from .documents import AddDocumentAjaxView, DeleteDocumentAjaxView
from .mixins import (
    AssessmentMixin,
    BarrierMixin,
    ResolvabilityAssessmentMixin,
    SessionDocumentMixin,
    StrategicAssessmentMixin,
)
from users.permissions import APIPermissionMixin
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


class ArchiveAssessmentBase(BarrierMixin, FormView):
    template_name = "barriers/assessments/archive.html"
    title = "Archive assessment"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["title"] = self.title
        return context_data

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


class ArchiveResolvabilityAssessment(APIPermissionMixin, ArchiveAssessmentBase):
    form_class = ArchiveResolvabilityAssessmentForm
    title = "Archive resolvability assessment"
    permission_required = "archive_resolvabilityassessment"


class ArchiveStrategicAssessment(APIPermissionMixin, ArchiveAssessmentBase):
    form_class = ArchiveStrategicAssessmentForm
    title = "Archive strategic assessment"
    permission_required = "archive_strategicassessment"


class ResolvabilityAssessmentDetail(ResolvabilityAssessmentMixin, BarrierMixin, TemplateView):
    template_name = "barriers/assessments/resolvability/detail.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["assessment"] = self.resolvability_assessment
        return context_data


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
