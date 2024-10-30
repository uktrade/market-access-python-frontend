import json

from django.urls import reverse
from django.views.generic import FormView, TemplateView

from users.account.forms import (
    UserEditPolicyTeamsForm,
    UserEditSectorsForm,
    UserEditBarrierLocationsForm,
    UserEditGovernmentDepartmentsForm,
    UserEditOverseasRegionsForm,
)
from utils.api.client import MarketAccessAPIClient
from utils.metadata import MetadataMixin


class UserEditBase(FormView, TemplateView, MetadataMixin):

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user_id"] = str(self.kwargs.get("user_id"))
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs
    
    def get_success_url(self):
        return reverse(
            "users:account",
        )

class UserEditPolicyTeams(UserEditBase):
    template_name = "users/account/edit_policy_teams.html"
    form_class = UserEditPolicyTeamsForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(
            {
                "select_options": self.metadata.get_policy_team_list(),
            }
        )
        return context_data

    def get_initial(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        current_user = client.users.get_current()
        selected_policy_teams = client.users.get(id=current_user.id).data["profile"][
            "policy_teams"
        ]
        return {
            "form": selected_policy_teams,
        }

    def form_valid(self, form):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        policy_teams = sorted(form.cleaned_data["form"])
        client.users.patch(
            id=str(self.kwargs.get("user_id")),
            profile={
                "id": str(self.kwargs.get("user_id")),
                "policy_teams": policy_teams,
            },
        )
        return super().form_valid(form)


class UserEditSectors(UserEditBase):
    template_name = "users/account/edit_sectors.html"
    form_class = UserEditSectorsForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        sectors = [{"id":item["id"], "title":item["name"]} for item in self.metadata.get_sector_list()]
        context_data.update(
            {
                "select_options": sectors,
            }
        )
        return context_data

    def get_initial(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        current_user = client.users.get_current()
        selected_sectors = client.users.get(id=current_user.id).data["profile"][
            "sectors"
        ]
        return {
            "form": json.dumps(selected_sectors),
        }

    def form_valid(self, form):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        sectors = sorted(form.cleaned_data["form"])
        client.users.patch(
            id=str(self.kwargs.get("user_id")),
            profile={
                "id": str(self.kwargs.get("user_id")),
                "sectors": sectors,
            },
        )
        return super().form_valid(form)
    

class UserEditOverseasRegions(UserEditBase):
    template_name = "users/account/edit_overseas_regions.html"
    form_class = UserEditOverseasRegionsForm


class UserEditBarrierLocations(UserEditBase):
    template_name = "users/account/edit_barrier_locations.html"
    form_class = UserEditBarrierLocationsForm


class UserEditGovernmentDepartments(UserEditBase):
    template_name = "users/account/edit_government_departments.html"
    form_class = UserEditGovernmentDepartmentsForm