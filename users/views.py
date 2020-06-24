import logging

import re
import requests
from urllib.parse import urlencode
import uuid

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, RedirectView, TemplateView

from .forms import UserGroupForm
from .mixins import GroupMixin, UserMixin, UserSearchMixin

from utils.api.client import MarketAccessAPIClient
from utils.exceptions import APIException
from utils.helpers import build_absolute_uri
from utils.sessions import init_session

logger = logging.getLogger(__name__)


class Login(RedirectView):
    def get(self, request, *args, **kwargs):
        self.state_id = str(uuid.uuid4())
        request.session["oauth_state_id"] = self.state_id
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self):
        redirect_uri = build_absolute_uri(self.request, "users:login_callback")
        params = {
            "response_type": "code",
            "client_id": settings.SSO_CLIENT,
            "redirect_uri": redirect_uri,
            "state": self.state_id,
        }
        if settings.SSO_MOCK_CODE:
            params["code"] = settings.SSO_MOCK_CODE

        return f"{settings.SSO_AUTHORIZE_URI}?{urlencode(params)}"


class LoginCallback(RedirectView):
    """
    Use the code in the querystring to get a token from the SSO server.

    If using Docker, this call comes from within the container, so
    SSO_TOKEN_URI has to be the internal address 'mocksso'.
    This is different to SSO_AUTHORIZE_URI, which is used in the browser, so
    has to be an external address.
    Because of this difference, we cannot easily use django-authbroker-client
    which assumes the same domain for both addresses.
    """

    def get(self, request, *args, **kwargs):
        if not request.session.get("oauth_state_id"):
            return HttpResponseRedirect(reverse("users:login"))

        self.check_for_errors()

        redirect_uri = build_absolute_uri(self.request, "users:login_callback")
        payload = {
            "code": request.GET.get("code"),
            "grant_type": "authorization_code",
            "client_id": settings.SSO_CLIENT,
            "client_secret": settings.SSO_SECRET,
            "redirect_uri": redirect_uri,
        }

        response = requests.post(url=settings.SSO_TOKEN_URI, data=payload)

        if response.status_code == 200:
            response_data = response.json()
            access_token = response_data.get("access_token")
            success = init_session(request.session, access_token)
            if success:
                return HttpResponseRedirect(self.get_redirect_url())
            else:
                raise PermissionDenied("Failed to initialise session.")
        else:
            error_msg = f"Status code: {response.status_code}, error: {response.text}"
            raise PermissionDenied("No access_token from SSO: %s", error_msg)

    def get_redirect_url(self):
        url = self.request.session.get("return_path")
        if url:
            del self.request.session["return_path"]
            return url

        return reverse("barriers:dashboard")

    def check_for_errors(self):
        error = self.request.GET.get("error")
        if error:
            raise PermissionDenied(f"Error with SSO: {error}")

        state_id = self.request.session.get("oauth_state_id")
        state = self.request.GET.get("state")
        if state != state_id:
            raise PermissionDenied(f"state_id mismatch: {state} != {state_id}")

        code = self.request.GET.get("code")
        if len(code) > settings.OAUTH_PARAM_LENGTH:
            raise PermissionDenied(f"Code too long: {len(code)}")

        if not re.match("^[a-zA-Z0-9-]+$", code):
            raise PermissionDenied(f"Invalid code: {code}")


class SignOut(RedirectView):
    def get(self, request, *args, **kwargs):
        uri = f"{settings.SSO_BASE_URI}logout/"
        request.session.flush()
        return HttpResponseRedirect(uri)


class ManageUsers(GroupMixin, TemplateView):
    template_name = "users/manage.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        groups = client.groups.list()

        context_data["groups"] = groups

        group_id = self.get_group_id()
        if group_id is None:
            context_data["users"] = client.users.list()
        else:
            context_data["group_id"] = group_id
        return context_data


class AddUser(UserSearchMixin, GroupMixin, FormView):
    template_name = "users/add.html"
    error_message = "There was an error adding {full_name} to the group."

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["group"] = self.group
        return context_data

    def select_user_api_call(self, user_id):
        group_id = self.get_group_id()
        if group_id:
            self.client.users.patch(id=user_id, groups=[{"id": group_id}])
        else:
            self.client.users.patch(id=user_id, groups=[])

    def get_success_url(self):
        success_url = reverse("users:manage_users")
        group_id = self.get_group_id()
        if group_id:
            return f"{success_url}?group={group_id}"
        return success_url


class EditUser(UserMixin, FormView):
    template_name = "users/edit.html"
    form_class = UserGroupForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        kwargs["id"] = str(self.kwargs.get("user_id"))
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["groups"] = client.groups.list()
        return kwargs

    def get_initial(self):
        for group in self.user.groups:
            return {"group": str(group["id"])}
        return {"group": "0"}

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("users:manage_users")


class UserDetail(UserMixin, TemplateView):
    template_name = "users/detail.html"
