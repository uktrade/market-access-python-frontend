from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, View

from utils.metadata import MetadataMixin

from ..forms.policy_teams import AddPolicyTeamForm, EditPolicyTeamsForm
from .mixins import BarrierMixin


class AddPolicyTeam(MetadataMixin, BarrierMixin, FormView):
    template_name = "barriers/edit/policy_teams/add.html"
    form_class = AddPolicyTeamForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update({"policy_teams": self.get_policy_team_list()})
        return context_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["policy_teams"] = self.get_policy_team_list()
        return kwargs

    def get_policy_team_list(self):
        """
        Get a list of all policy teams excluding any already selected
        """
        selected_policy_team_ids = [
            str(policy_team["id"])
            for policy_team in self.request.session.get("policy_teams", [])
        ]

        return [
            policy_team
            for policy_team in self.metadata.get_policy_team_list()
            if str(policy_team["id"]) not in selected_policy_team_ids
        ]

    def form_valid(self, form):
        """
        Add the new policy team to the session and redirect
        """
        policy_team = self.metadata.get_policy_team(form.cleaned_data["policy_team"])
        policy_teams = self.request.session.get("policy_teams", [])
        policy_teams.append(
            {
                "id": policy_team["id"],
                "title": policy_team["title"],
            }
        )
        
        self.request.session["policy_teams"] = sorted(policy_teams, key=lambda k: k["title"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:edit_policy_teams_session",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class BarrierEditPolicyTeams(MetadataMixin, BarrierMixin, FormView):
    template_name = "barriers/edit/policy_teams/edit.html"
    form_class = EditPolicyTeamsForm
    use_session_policy_teams = False

    def get(self, request, *args, **kwargs):
        if not self.use_session_policy_teams:
            request.session["policy_teams"] = self.barrier.policy_teams
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update({"policy_teams": self.request.session.get("policy_teams", [])})
        return context_data

    def get_initial(self):
        policy_teams = self.request.session.get("policy_teams", [])
        return {
            "policy_teams": [policy_team["id"] for policy_team in policy_teams],
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["barrier_id"] = str(self.kwargs.get("barrier_id"))
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["policy_teams"] = self.metadata.get_policy_team_list()
        return kwargs

    def form_valid(self, form):
        form.save()
        try:
            del self.request.session["policy_teams"]
        except KeyError:
            pass
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class BarrierEditPolicyTeamsSession(BarrierEditPolicyTeams):
    use_session_policy_teams = True


class BarrierRemovePolicyTeam(View):
    """
    Remove the policy team from the session and redirect
    """

    def post(self, request, *args, **kwargs):
        policy_teams = self.request.session.get("policy_teams", [])
        policy_team_id = request.POST.get("policy_team_id")

        self.request.session["policy_teams"] = [
            policy_team for policy_team in policy_teams if policy_team_id != str(policy_team["id"])
        ]
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "barriers:edit_policy_teams_session",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
