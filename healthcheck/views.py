import time

from django.views.generic import TemplateView

from authentication.decorators import public_view
from healthcheck.constants import HealthStatus

from .checks import api_check, db_check


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


@public_view
class APIHealthCheckView(TemplateView):
    template_name = "healthcheck.html"

    def get_context_data(self, **kwargs):
        """ Adds status and response time to response context """
        context = super().get_context_data(**kwargs)
        fe_response_time = time.time() - self.request.start_time
        data = api_check()
        context["status"] = data.get("status") or HealthStatus.FAIL
        context["response_time"] = data.get("duration") or fe_response_time
        return context
