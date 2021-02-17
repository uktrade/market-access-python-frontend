from django.conf import settings
from django.views.generic import TemplateView

from ..mixins import BarrierMixin


class AssessmentOverview(BarrierMixin, TemplateView):
    template_name = "barriers/assessments/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        assement_class = "assessment-item"
        # If not configured, hide
        if not settings.PRIORITISATION_STRATEGIC_ASSESSMENTS:
            assement_class += " visually-hidden"

        context["strategic_ass"] = assement_class
        return context
