from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from ..forms.teams import AddTeamMemberForm, UserSearchForm
from .mixins import BarrierMixin, TeamMembersContextMixin

from utils.api.client import MarketAccessAPIClient
from utils.exceptions import APIException
from utils.sso import SSOClient


class BarrierTeam(TeamMembersContextMixin, BarrierMixin, TemplateView):
    template_name = "barriers/team.html"


class SearchTeamMember(BarrierMixin, FormView):
    template_name = "barriers/teams/search.html"
    form_class = UserSearchForm

    def add_member(self, form):
        user_id = form.data["user_id"]
        full_name = form.data["user_full_name"]
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        try:
            client.barriers.add_team_member(
                barrier_id=str(self.kwargs.get("barrier_id")),
                user_id=user_id,
                role="Contributor",
            )
            self.success_url = reverse(
                "barriers:team", kwargs={"barrier_id": self.kwargs.get("barrier_id")}
            )
            return super().form_valid(form)
        except APIException:
            error = f"There was an error adding {full_name} to the team."
            return self.render_to_response(
                self.get_context_data(form=form, results=(), error=error)
            )

    def form_valid(self, form):
        action = self.request.POST.get("action")
        if action == "add":
            return self.add_member(form)
        else:
            # Search
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


class ChangeOwnerView(BarrierMixin, FormView):
    template_name = "barriers/teams/change_owner.html"
    form_class = UserSearchForm

    def get(self, *args, **kwargs):
        team_member_id = kwargs.get('team_member_id')
        if not team_member_id:
            return HttpResponseRedirect(self.get_success_url())
        context = self.get_context_data(team_member_id)
        return self.render_to_response(context)

    def get_context_data(self, team_member_id, **kwargs):
        context_data = super().get_context_data(**kwargs)
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        context_data["owner"] = client.barriers.get_team_member(team_member_id)
        return context_data

    def new_owner(self, team_member_id, form):
        user_id = form.data["user_id"]
        full_name = form.data["user_full_name"]
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        try:
            client.barriers.patch_team_member(
                team_member_id,
                {"user": user_id}
            )
            return super().form_valid(form)
        except APIException:
            error = f"There was an error adding {full_name} as the new owner."
            return self.render_to_response(
                self.get_context_data(
                    form=form, results=(), error=error, team_member_id=team_member_id
                )
            )

    def form_valid(self, form):
        team_member_id = self.kwargs.get('team_member_id')
        action = self.request.POST.get("action")

        if action == "add":
            return self.new_owner(team_member_id, form)
        else:
            client = SSOClient()
            error = None

            try:
                results = client.search_users(form.cleaned_data["query"])
            except APIException:
                error = "There was an error searching for users"
                results = []

            return self.render_to_response(
                self.get_context_data(
                    form=form, results=results, error=error, team_member_id=team_member_id
                )
            )

    def get_success_url(self):
        return reverse(
            "barriers:team", kwargs={"barrier_id": self.kwargs.get("barrier_id")}
        )


class DeleteTeamMember(
    TeamMembersContextMixin, BarrierMixin, TemplateView,
):
    template_name = "barriers/teams/delete_member.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["team_member"] = self.get_team_member(
            self.kwargs.get("team_member_id")
        )
        return context_data

    def post(self, request, *args, **kwargs):
        team_member_id = self.kwargs.get("team_member_id")
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        client.barriers.delete_team_member(team_member_id)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "barriers:team", kwargs={"barrier_id": self.kwargs.get("barrier_id")}
        )
