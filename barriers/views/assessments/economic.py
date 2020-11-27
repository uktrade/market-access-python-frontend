from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, RedirectView, TemplateView

from .base import ArchiveAssessmentBase
from ..documents import AddDocumentAjaxView, DeleteDocumentAjaxView
from ..mixins import BarrierMixin, EconomicAssessmentMixin, SessionDocumentMixin
from ...forms.assessments.economic import (
    ArchiveEconomicAssessmentForm,
    EconomicAssessmentDocumentForm,
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
        elif self.kwargs.get("barrier_id"):
            kwargs["barrier"] = self.barrier
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
            "barriers:add_economic_assessment_rating",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class EditEconomicAssessmentRating(APIPermissionMixin, EconomicAssessmentEditBase):
    template_name = "barriers/assessments/economic/edit_rating.html"
    permission_required = "change_economicassessment"
    form_class = EconomicAssessmentRatingForm

    def get_initial(self):
        if not self.kwargs.get("assessment_id"):
            return {}

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


class AutomateEconomicAssessment(APIPermissionMixin, EconomicAssessmentMixin, BarrierMixin, TemplateView):
    template_name = "barriers/assessments/economic/automate.html"
    permission_required = "add_economicassessment"

    def post(self, request, *args, **kwargs):
        # Disable automated assessments until sensitivity issues are resolved
        if False:
            client = MarketAccessAPIClient(self.request.session.get("sso_token"))
            economic_assessment = client.economic_assessments.create(
                barrier_id=self.barrier.id,
                automate=True,
            )
            return HttpResponseRedirect(self.get_success_url(economic_assessment))
        return self.get(request, *args, **kwargs)

    def get_success_url(self, economic_assessment):
        return reverse(
            "barriers:edit_economic_assessment_rating",
            kwargs={
                "barrier_id": self.kwargs.get("barrier_id"),
                "assessment_id": economic_assessment.id,
            },
        )


class EconomicAssessmentRawData(EconomicAssessmentMixin, BarrierMixin, TemplateView):
    template_name = "barriers/assessments/economic/raw_data.html"


class ArchiveEconomicAssessment(APIPermissionMixin, ArchiveAssessmentBase):
    form_class = ArchiveEconomicAssessmentForm
    title = "Archive economic assessment"
    permission_required = "archive_economicassessment"


class AssessmentSessionDocumentMixin(SessionDocumentMixin):
    def get_session_key(self):
        barrier_id = self.kwargs.get("barrier_id")
        assessment_id = self.kwargs.get("assessment_id", "new")
        return f"barrier:{barrier_id}:economic_assessments:{assessment_id}:documents"


class AddEconomicAssessmentDocument(
    AssessmentSessionDocumentMixin, AddDocumentAjaxView,
):
    form_class = EconomicAssessmentDocumentForm

    def get_delete_url(self, document):
        return reverse(
            "barriers:delete_economic_assessment_document",
            kwargs={
                "barrier_id": self.kwargs.get("barrier_id"),
                "document_id": document["id"],
            },
        )


class DeleteEconomicAssessmentDocument(
    AssessmentSessionDocumentMixin, DeleteDocumentAjaxView,
):
    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            "barriers:economic_assessment",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class CancelEconomicAssessmentDocument(AssessmentSessionDocumentMixin, RedirectView):
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
