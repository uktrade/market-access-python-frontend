import json

import sentry_sdk
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from authentication.decorators import public_view


@public_view
@method_decorator(csrf_exempt, name="dispatch")
class CSPReportView(View):
    def post(self, request, *args, **kwargs):
        sentry_sdk.api.capture_message(json.loads(request.body.decode("utf-8")))
        return HttpResponse(status=200)
