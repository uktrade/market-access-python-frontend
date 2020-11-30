from django.views.generic import TemplateView

from ..mixins import BarrierMixin


class AssessmentOverview(BarrierMixin, TemplateView):
    template_name = "barriers/assessments/overview.html"
