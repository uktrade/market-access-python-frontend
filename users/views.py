import re
import uuid
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, RedirectView, TemplateView

from utils.api.client import MarketAccessAPIClient
from utils.helpers import build_absolute_uri
from utils.pagination import PaginationMixin
from utils.referers import RefererMixin
from utils.sessions import init_session
from utils.sso import SSOClient

from .forms import UserGroupForm
from .mixins import GroupQuerystringMixin, UserMixin, UserSearchMixin
from .permissions import APIPermissionMixin


class GetUsers(View):
    def serialize_results(self, results):
        return [
            {
                "user_id": str(result["user_id"]),
                "first_name": result["first_name"],
                "last_name": result["last_name"],
                "email": result["email"],
            }
            for result in results
        ]

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q")
        response = {"count": 0, "results": []}
        if not query:
            return JsonResponse(response)

        # search needs to have email dots replaced with spaces for search lookup
        query = query.replace(".", " ")

        sso_client = SSOClient()
        results = sso_client.search_users(query)
        serialized_results = self.serialize_results(results)
        response["results"] = serialized_results
        response["count"] = len(results)
        return JsonResponse(response)


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

        response = requests.post(url=settings.SSO_TOKEN_URI, data=payload, timeout=10)
        if response.status_code != 200:
            error_msg = f"No access_token from SSO: Status code: {response.status_code}, error: {response.text}"
            raise PermissionDenied(error_msg)

        response_data = response.json()
        access_token = response_data.get("access_token")
        success = init_session(request.session, access_token)
        if not success:
            raise PermissionDenied("Failed to initialise session.")

        return HttpResponseRedirect(self.get_redirect_url())

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


class ManageUsers(
    APIPermissionMixin,
    PaginationMixin,
    GroupQuerystringMixin,
    TemplateView,
):
    template_name = "users/manage.html"
    permission_required = "list_users"
    pagination_limit = 500

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        group_id = self.get_group_id()

        context_data["page"] = "manage-users"
        context_data["groups"] = client.groups.list()
        if group_id is None:
            users = client.users.list(
                limit=self.get_pagination_limit(),
                offset=self.get_pagination_offset(),
            )
            context_data["users"] = users
            context_data["pagination"] = self.get_pagination_data(object_list=users)
        else:
            context_data["group_id"] = group_id

        return context_data


class AddUser(APIPermissionMixin, UserSearchMixin, GroupQuerystringMixin, FormView):
    template_name = "users/add.html"
    error_message = "There was an error adding {full_name} to the group."
    permission_required = "change_user"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["group"] = self.group
        context_data["page"] = "manage-users"
        return context_data

    def select_user_api_call(self, user_id):
        group_id = self.get_group_id()
        user = self.client.users.get(user_id)
        if group_id:
            user_groups = user.groups
            groups = self.client.groups.list()
            group_name = [
                group.data["name"] for group in groups if group.data["id"] == group_id
            ][0]
            is_permission_bundle_group = (
                group_name in settings.USER_ADDITIONAL_PERMISSION_GROUPS
            )

            if is_permission_bundle_group:
                groups = [{"id": group["id"]} for group in user_groups] + [
                    {"id": group_id}
                ]
            else:
                groups = [{"id": group_id}]

            self.client.users.patch(id=user_id, groups=groups)
            return

        # This call creates a user if they don't exist
        self.client.users.get(id=user_id)

    def get_success_url(self):
        success_url = reverse("users:manage_users")
        group_id = self.get_group_id()
        if group_id:
            return f"{success_url}?group={group_id}"
        return success_url


class EditUser(APIPermissionMixin, RefererMixin, UserMixin, FormView):
    template_name = "users/edit.html"
    form_class = UserGroupForm
    permission_required = "change_user"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["page"] = "manage-users"
        return context_data

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
        return HttpResponseRedirect(
            self.get_success_url(new_group_id=form.cleaned_data.get("group"))
        )

    def get_success_url(self, new_group_id):
        if not self.referer.path:
            return reverse(
                "users:user_detail", kwargs={"user_id": self.kwargs.get("user_id")}
            )

        if self.referer.url_name != "manage_users":
            return self.referer.path

        manage_users_url = reverse("users:manage_users")
        if new_group_id != "0":
            return f"{manage_users_url}?group={new_group_id}"

        return manage_users_url


class UserDetail(UserMixin, TemplateView):
    template_name = "users/detail.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["page"] = "manage-users"
        return context_data
