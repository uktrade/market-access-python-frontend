from django.urls import reverse
from django.views.generic import FormView, TemplateView

from users.profile.forms.policy_teams import UserEditPolicyTeamsForm
from utils.api.client import MarketAccessAPIClient
from utils.metadata import MetadataMixin


class UserEditPolicyTeams(FormView, TemplateView, MetadataMixin):
    template_name = "users/policy_teams/edit_policy_teams.html"
    form_class = UserEditPolicyTeamsForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user_id"] = str(self.kwargs.get("user_id"))
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(
            {
                "policy_teams": self.metadata.get_policy_team_list(),
            }
        )
        return context_data

    def form_valid(self, form):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        policy_teams = sorted(form.cleaned_data["policy_teams"])
        print(policy_teams)
        client.users.patch(
            id=str(self.kwargs.get("user_id")),
            policy_teams=policy_teams,
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "users:account",
        )
