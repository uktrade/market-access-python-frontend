import time

from django.views.generic import TemplateView

from authentication.decorators import public_view
from .checks import db_check


@public_view
class HealthCheckView(TemplateView):
    template_name = "healthcheck.html"

    def get_context_data(self, **kwargs):
        """ Adds status and response time to response context """
        context = super().get_context_data(**kwargs)
        context["status"] = db_check()
        # nearest approximation of a response time
        context["response_time"] = time.time() - self.request.start_time
        return context
