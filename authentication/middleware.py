import logging

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
        logging.warning(f"STUB:1 {getattr(request,'user',None)}")
        tmp = self.get_response(request)
        logging.warning(f"STUB:2 {getattr(request,'user',None)}")
        logging.warning(f"STUB:3 {tmp.__dict__}")
        return tmp

    def process_view(self, request, view_func, view_args, view_kwargs):
        public_view = getattr(view_func.view_class, "_public_view", False)
        if public_view:
            return view_func(request, *view_args, **view_kwargs)

        sso_token = request.session.get("sso_token")
        user_data = request.session.get("user_data")
        is_authenticated = sso_token and user_data
        is_login_path = request.path in (
            reverse("users:login"),
            reverse("users:login_callback"),
        )
        is_static = request.path.startswith((settings.STATIC_URL, "/govuk-public"))

        if is_authenticated or is_login_path or is_static:
            # return None to allow this to continue as per Django docs
            # https://docs.djangoproject.com/en/3.0/topics/http/middleware/#process-view
            # If it returns None, Django will continue processing this request, executing any other process_view()
            # middleware and, then, the appropriate view.
            return None

        request.session["return_path"] = request.path
        return HttpResponseRedirect(reverse("users:login"))

    def process_exception(self, request, exception):
        if not isinstance(exception, APIHttpException):
            return

        if exception.status_code != HTTPStatus.UNAUTHORIZED:
            return

        try:
            del request.session["sso_token"]
        except KeyError:
            pass
        request.session["return_path"] = request.path
        return HttpResponseRedirect(reverse("users:login"))
