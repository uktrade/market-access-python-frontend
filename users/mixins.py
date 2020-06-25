from django.http import HttpResponseRedirect

from .forms import UserSearchForm

from utils.api.client import MarketAccessAPIClient
from utils.exceptions import APIException
from utils.sso import SSOClient


class UserMixin:
    _user = None

    @property
    def user(self):
        if not self._user:
            self._user = self.get_user()
        return self._user

    def get_user(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        user_id = self.kwargs.get("user_id")
        return client.users.get(user_id)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["user"] = self.user
        return context_data


class UserSearchMixin:
    form_class = UserSearchForm
    error_message = "There was an error adding {full_name}"

    @property
    def client(self):
        return MarketAccessAPIClient(self.request.session.get("sso_token"))

    def form_valid(self, form):
        if self.request.POST.get("action") == "add":
            return self.select_user(form)

        client = SSOClient()
        error = None

        try:
            results = client.search_users(form.cleaned_data["query"])
        except APIException as e:
            error = "There was an error searching for users"
            results = []

        return self.render_to_response(
            self.get_context_data(form=form, results=results, error=error)
        )

    def select_user(self, form):
        user_id = form.data["user_id"]
        full_name = form.data["user_full_name"]
        try:
            self.select_user_api_call(user_id)
            return HttpResponseRedirect(self.get_success_url())
        except APIException:
            error = self.error_message.format(full_name=full_name)
            return self.render_to_response(
                self.get_context_data(form=form, results=(), error=error)
            )

    def select_user_api_call(self, *args, **kwargs):
        raise NotImplementedError


class GroupQuerystringMixin:
    _group = None

    def get_group_id(self):
        if "group" in self.request.GET:
            try:
                return int(self.request.GET.get("group"))
            except ValueError:
                return None

    @property
    def group(self):
        if not self._group:
            self._group = self.get_group()
        return self._group

    def get_group(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        group_id = self.get_group_id()
        if group_id:
            return client.groups.get(group_id)
