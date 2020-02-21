from http import HTTPStatus

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse

from utils.exceptions import APIHttpException


class SSOMiddleware:
    """
    Middleware to ensure user has an SSO token an user_data in the session is populated.

    If the user has no SSO token or user_data, store the current path in the session
    and redirect to the SSO login page.
    The user will return to the stored path after SSO login.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        sso_token = request.session.get("sso_token")
        user_data = request.session.get("user_data")
        is_authenticated = sso_token and user_data
        is_login_path = request.path in (
            reverse("users:login"),
            reverse("users:login_callback"),
        )
        is_static = request.path.startswith((settings.STATIC_URL, "/govuk-public"))

        if is_authenticated or is_login_path or is_static:
            return self.get_response(request)

        request.session["return_path"] = request.path
        return HttpResponseRedirect(reverse("users:login"))

    def process_exception(self, request, exception):
        if isinstance(exception, APIHttpException):
            if exception.status_code == HTTPStatus.UNAUTHORIZED:
                try:
                    del request.session["sso_token"]
                except KeyError:
                    pass
                request.session["return_path"] = request.path
                return HttpResponseRedirect(reverse("users:login"))
