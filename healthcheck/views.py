import time

from django.views.generic import TemplateView
from sentry_sdk import capture_exception

from authentication.decorators import public_view
from healthcheck.models import HealthCheck


class HealthStatus:
    OK = "OK"
    FAIL = "FAIL"

@public_view
class HealthCheckView(TemplateView):
    template_name = "healthcheck.html"

    def _db_check(self):
        """
        Performs a basic check on the database by performing a select query on a simple table
        :return: True or False according to successful retrieval
        """
        try:
            HealthCheck.objects.get(health_check_field=True)
            return HealthStatus.OK
        except Exception as e:
            capture_exception(e)
            return HealthStatus.FAIL

    def get_context_data(self, **kwargs):
        """ Adds status and response time to response context"""
        context = super().get_context_data(**kwargs)
        context["status"] = self._db_check()
        # nearest approximation of a response time
        context["response_time"] = time.time() - self.request.start_time
        return context
