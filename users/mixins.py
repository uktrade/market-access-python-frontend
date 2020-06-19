from .forms import UserSearchForm

from utils.exceptions import APIException
from utils.sso import SSOClient


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
