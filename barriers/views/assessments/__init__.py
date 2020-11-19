from django.urls import reverse
from django.views.generic import TemplateView

from ..mixins import BarrierMixin


class AssessmentDetail(BarrierMixin, TemplateView):
    template_name = "barriers/assessments/detail.html"
