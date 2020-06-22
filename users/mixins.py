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

    def select_user(self, form):
        raise NotImplementedError

    def form_valid(self, form):
        if self.request.POST.get("action") == "add":
            return self.select_user(form)

        client = SSOClient()
        error = None

        try:
            results = client.search_users(form.cleaned_data["query"])
        except APIException:
            error = "There was an error searching for users"
            results = []

        return self.render_to_response(
            self.get_context_data(form=form, results=results, error=error)
        )
