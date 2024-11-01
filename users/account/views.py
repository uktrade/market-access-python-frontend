import json

from django.urls import reverse
from django.views.generic import FormView, TemplateView

from users.account.forms import (
    UserEditBarrierLocationsForm,
    UserEditGovernmentDepartmentsForm,
    UserEditOverseasRegionsForm,
    UserEditPolicyTeamsForm,
    UserEditSectorsForm,
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
        policy_teams = [
            (policy_team["id"], policy_team["title"])
            for policy_team in self.metadata.get_policy_team_list()
        ]
        context_data.update(
            {
                "select_options": policy_teams,
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
        sectors = [
            (sector["id"], sector["name"])
            for sector in self.metadata.get_sector_list(level=0)
        ]
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

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(
            {
                "select_options": self.metadata.get_overseas_region_choices(),
            }
        )
        return context_data

    def get_initial(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        current_user = client.users.get_current()
        overseas_regions = client.users.get(id=current_user.id).data["profile"][
            "overseas_regions"
        ]
        return {
            "form": json.dumps(overseas_regions),
        }

    def form_valid(self, form):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        overseas_regions = sorted(form.cleaned_data["form"])
        client.users.patch(
            id=str(self.kwargs.get("user_id")),
            profile={
                "id": str(self.kwargs.get("user_id")),
                "overseas_regions": overseas_regions,
            },
        )
        return super().form_valid(form)


class UserEditBarrierLocations(UserEditBase):
    template_name = "users/account/edit_barrier_locations.html"
    form_class = UserEditBarrierLocationsForm


class UserEditGovernmentDepartments(FormView, MetadataMixin):
    template_name = "users/account/edit_government_departments.html"
    form_class = UserEditGovernmentDepartmentsForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user_id"] = str(self.kwargs.get("user_id"))
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["government_departments"] = [
            (organisation_id, organisation_name)
            for organisation_id, organisation_name in self.metadata.get_gov_organisation_choices()
        ]
        return kwargs

    def form_valid(self, form):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        print(form.cleaned_data["government_departments"])
        client.users.patch(
            id=str(self.kwargs.get("user_id")),
            profile={
                "id": str(self.kwargs.get("user_id")),
                "organisations": [form.cleaned_data["government_departments"]],
            },
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "users:account",
        )