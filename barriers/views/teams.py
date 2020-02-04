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

    def form_valid(self, form):
        client = SSOClient()
        error = None

        try:
            results = client.search_users(form.cleaned_data['query'])
        except APIException:
            error = "There was an error searching for users"
            results = []

        return self.render_to_response(
            self.get_context_data(form=form, results=results, error=error)
        )


class AddTeamMember(TeamMembersContextMixin, BarrierMixin, FormView):
    template_name = "barriers/teams/add_member.html"
    form_class = AddTeamMemberForm

    def get(self, request, *args, **kwargs):
        user_id = self.request.GET.get('user')
        if not user_id:
            return HttpResponseRedirect(self.get_success_url())
        context = self.get_context_data(user_id, **kwargs)
        return self.render_to_response(context)

    def get_context_data(self, user_id, **kwargs):
        context_data = super().get_context_data(**kwargs)
        client = MarketAccessAPIClient(self.request.session.get('sso_token'))
        context_data['user'] = client.users.get(user_id)
        return context_data

    def get_initial(self):
        return {'user': self.request.GET.get('user')}

    def form_invalid(self, form):
        user_id = self.request.GET.get('user')
        return self.render_to_response(
            self.get_context_data(user_id=user_id, form=form)
        )

    def form_valid(self, form):
        client = MarketAccessAPIClient(self.request.session.get('sso_token'))
        client.barriers.add_team_member(
            barrier_id=str(self.kwargs.get('barrier_id')),
            user_id=form.cleaned_data['user'],
            role=form.cleaned_data['role'],
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'barriers:team',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )


class DeleteTeamMember(
    TeamMembersContextMixin,
    BarrierMixin,
    TemplateView,
):
    template_name = "barriers/teams/delete_member.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['team_member'] = self.get_team_member(
            self.kwargs.get('team_member_id')
        )
        return context_data

    def post(self, request, *args, **kwargs):
        team_member_id = self.kwargs.get('team_member_id')
        client = MarketAccessAPIClient(self.request.session.get('sso_token'))
        client.barriers.delete_team_member(team_member_id)
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            'barriers:team',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )
