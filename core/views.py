import json
import logging

import sentry_sdk
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from authentication.decorators import public_view

logger = logging.getLogger(__name__)


@public_view
@method_decorator(csrf_exempt, name="dispatch")
class CSPReportView(View):
    def post(self, request, *args, **kwargs):
        report = json.loads(request.body.decode("utf-8"))["csp-report"]
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("type", "csp_report")
            extra = {
                "blocked_uri": report.get("blocked-uri"),
                "document_uri": report.get("document-uri"),
                "line_number": report.get("line-number"),
                "effective_directive": report.get("effective-directive"),
            }
            logger.error("CSP Blocked", extra=extra)
        return HttpResponse(status=200)
