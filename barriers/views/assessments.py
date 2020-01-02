from http import HTTPStatus

from django.conf import settings
from django.http import JsonResponse
from django.template.defaultfilters import filesizeformat
from django.urls import reverse
from django.views.generic import FormView, RedirectView, TemplateView

from ..forms.assessments import (
    CommercialValueForm,
    DocumentForm,
    EconomicAssessmentForm,
    EconomyValueForm,
    ExportValueForm,
    MarketSizeForm,
)
from .mixins import AssessmentMixin, BarrierContextMixin

from utils.exceptions import FileUploadError, ScanError


class AssessmentDetail(AssessmentMixin, BarrierContextMixin, TemplateView):
    template_name = "barriers/assessments/detail.html"


class EconomicAssessment(AssessmentMixin, BarrierContextMixin, FormView):
    template_name = "barriers/assessments/economic.html"
    form_class = EconomicAssessmentForm

    def get(self, request, *args, **kwargs):
        if self.assessment:
            if 'assessment_documents' not in self.request.session:
                self.request.session['assessment_documents'] = (
                    self.assessment.documents
                )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['documents'] = (
            self.request.session.get('assessment_documents', [])
        )
        context_data['max_file_size'] = settings.FILE_MAX_SIZE
        return context_data

    def get_initial(self):
        if self.assessment:
            return {
                'impact': self.assessment.impact,
                'description': self.assessment.explanation,
            }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['barrier'] = self.barrier
        kwargs['token'] = self.request.session.get('sso_token')
        return kwargs

    def form_valid(self, form):
        form.save()
        del self.request.session['assessment_documents']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'barriers:assessment_detail',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )


class NewEconomicAssessment(RedirectView):
    """
    Clears the session and redirects to the economic assessment page
    """
    def get(self, request, *args, **kwargs):
        try:
            del self.request.session['assessment_documents']
        except KeyError:
            pass
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            'barriers:economic_assessment',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )


class AddAssessmentDocument(FormView):
    """
    Ajax view for uploading documents
    """
    form_class = DocumentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['token'] = self.request.session.get('sso_token')
        return kwargs

    def form_valid(self, form):
        try:
            document = form.save()
        except FileUploadError as e:
            return JsonResponse(
                {"message": str(e)},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        except ScanError as e:
            return JsonResponse(
                {"message": str(e)},
                status=HTTPStatus.UNAUTHORIZED,
            )

        self.add_document_to_session(document)

        return JsonResponse({
            "documentId": document['id'],
            "file": {
                "name": document['file']['name'],
                "size": filesizeformat(document['file']['size']),
            }
        })

    def add_document_to_session(self, document):
        documents = self.request.session.get('assessment_documents', [])
        documents.append({
            'id': document['id'],
            'name': document['file']['name'],
            'size': document['file']['size'],
        })
        self.request.session['assessment_documents'] = documents

    def form_invalid(self, form):
        return JsonResponse({
            "message": ", ".join(form.errors.get('document', [])),
        }, status=HTTPStatus.BAD_REQUEST)


class DeleteAssessmentDocument(RedirectView):
    """
    Deletes an assessment document from the session.

    Can be called via ajax or as a get request.
    """
    def delete_document_from_session(self):
        document_id = self.kwargs.get('document_id')
        documents = self.request.session['assessment_documents']

        self.request.session['assessment_documents'] = [
            document
            for document in documents
            if document['id'] != str(document_id)
        ]

    def get(self, request, *args, **kwargs):
        self.delete_document_from_session()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.delete_document_from_session()
        return JsonResponse({})

    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            'barriers:economic_assessment',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )


class AssessmentValueView(AssessmentMixin, BarrierContextMixin, FormView):
    """
    Base class to be used by views which update one field of an Assessment
    """
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['barrier'] = self.barrier
        kwargs['token'] = self.request.session.get('sso_token')
        return kwargs

    def get_initial(self):
        return {'value': self.assessment.value_to_economy}

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'barriers:assessment_detail',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )


class EconomyValueAssessment(AssessmentValueView, FormView):
    template_name = "barriers/assessments/economy_value.html"
    form_class = EconomyValueForm

    def get_initial(self):
        if self.assessment:
            return {
                'value': self.assessment.value_to_economy
            }


class MarketSizeAssessment(AssessmentValueView, FormView):
    template_name = "barriers/assessments/market_size.html"
    form_class = MarketSizeForm

    def get_initial(self):
        if self.assessment:
            return {
                'value': self.assessment.import_market_size
            }


class CommercialValueAssessment(AssessmentValueView):
    template_name = "barriers/assessments/commercial_value.html"
    form_class = CommercialValueForm

    def get_initial(self):
        if self.assessment:
            return {'value': self.assessment.commercial_value}


class ExportValueAssessment(AssessmentValueView):
    template_name = "barriers/assessments/export_value.html"
    form_class = ExportValueForm

    def get_initial(self):
        if self.assessment:
            return {'value': self.assessment.export_value}
