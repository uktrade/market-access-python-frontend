from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from ..forms.assessments import (
    CommercialValueForm,
    EconomicAssessmentForm,
    EconomyValueForm,
    ExportValueForm,
    MarketSizeForm,
)
from .mixins import AssessmentMixin, BarrierContextMixin


class AssessmentDetail(AssessmentMixin, BarrierContextMixin, TemplateView):
    template_name = "barriers/assessments/detail.html"


class EconomicAssessment(AssessmentMixin, BarrierContextMixin, FormView):
    template_name = "barriers/assessments/economic.html"
    form_class = EconomicAssessmentForm

    def get_initial(self):
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
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'barriers:assessment_detail',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )


class AddAssessmentDocument(TemplateView):
    def post(self, request, *args, **kwargs):
        return JsonResponse({})


class DeleteAssessmentDocument(TemplateView):
    def post(self, request, *args, **kwargs):
        return JsonResponse({})


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
        return {
            'value': self.assessment.value_to_economy
        }


class MarketSizeAssessment(AssessmentValueView, FormView):
    template_name = "barriers/assessments/market_size.html"
    form_class = MarketSizeForm

    def get_initial(self):
        return {
            'value': self.assessment.import_market_size
        }


class CommercialValueAssessment(AssessmentValueView):
    template_name = "barriers/assessments/commercial_value.html"
    form_class = CommercialValueForm

    def get_initial(self):
        return {'value': self.assessment.commercial_value}


class ExportValueAssessment(AssessmentValueView):
    template_name = "barriers/assessments/export_value.html"
    form_class = ExportValueForm

    def get_initial(self):
        return {'value': self.assessment.export_value}
