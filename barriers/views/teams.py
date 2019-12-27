from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from ..forms.teams import AddTeamMemberForm, UserSearchForm
from .mixins import BarrierContextMixin, TeamMembersContextMixin

from utils.api_client import MarketAccessAPIClient
from utils.sso import SSOClient


class BarrierTeam(TeamMembersContextMixin, BarrierContextMixin, TemplateView):
    template_name = "barriers/team.html"
    include_interactions = False


class SearchTeamMember(BarrierContextMixin, FormView):
    template_name = "barriers/teams/search.html"
    form_class = UserSearchForm
    include_interactions = False

    def form_valid(self, form):
        client = SSOClient()
        results = client.search_users(form.cleaned_data['query'])
        return self.render_to_response(
            self.get_context_data(form=form, results=results)
        )


class AddTeamMember(TeamMembersContextMixin, BarrierContextMixin, FormView):
    template_name = "barriers/teams/add_member.html"
    form_class = AddTeamMemberForm
    include_interactions = False

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        user_id = self.request.GET.get('user')
        client = MarketAccessAPIClient(self.request.session.get('sso_token'))
        context_data['user'] = client.get(f'users/{user_id}')
        return context_data

    def get_initial(self):
        return {'user': self.request.GET.get('user')}

    def form_valid(self, form):
        client = MarketAccessAPIClient(self.request.session.get('sso_token'))
        client.barriers.add_team_member(
            barrier_id=self.kwargs.get('barrier_id'),
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
    BarrierContextMixin,
    TemplateView
):
    template_name = "barriers/teams/delete_member.html"
    include_interactions = False

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
