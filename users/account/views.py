import json

from django.urls import reverse
from django.views.generic import FormView, TemplateView

from users.account.forms import (
    UserEditBarrierLocationsForm,
    UserEditGovernmentDepartmentForm,
    UserEditOverseasRegionsForm,
    UserEditPolicyTeamsForm,
    UserEditSectorsForm,
)
from utils.api.client import MarketAccessAPIClient
from utils.metadata import MetadataMixin

# TODO refactor to reduce duplication across views


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

    def get_selected_options(self, area):
        self.client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        self.current_user = self.client.users.get_current()
        return self.client.profile.get(id=self.current_user.id).data[area]


class UserEditPolicyTeams(UserEditBase):
    template_name = "users/account/edit_policy_teams.html"
    form_class = UserEditPolicyTeamsForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        policy_teams = [
            (policy_team["id"], policy_team["title"])
            for policy_team in self.metadata.get_policy_team_list()
        ]
        context_data.update({"select_options": policy_teams})
        return context_data

    def get_initial(self):
        return {
            "form": [
                policy_team["id"]
                for policy_team in self.get_selected_options("policy_teams")
            ],
        }

    def form_valid(self, form):
        self.client.profile.patch(
            id=str(self.current_user.id),
            policy_teams=sorted(form.cleaned_data["form"]),
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
        return {
            "form": json.dumps(
                [sector["id"] for sector in self.get_selected_options("sectors")]
            ),
        }

    def form_valid(self, form):
        self.client.profile.patch(
            id=str(self.current_user.id),
            sectors=sorted(form.cleaned_data["form"]),
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
        return {
            "form": json.dumps(
                [
                    region["id"]
                    for region in self.get_selected_options("overseas_regions")
                ]
            ),
        }

    def form_valid(self, form):
        self.client.profile.patch(
            id=str(self.current_user.id),
            overseas_regions=sorted(form.cleaned_data["form"]),
        )
        return super().form_valid(form)


class UserEditBarrierLocations(UserEditBase):
    template_name = "users/account/edit_barrier_locations.html"
    form_class = UserEditBarrierLocationsForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        locations = (
            (
                "Trading blocs",
                tuple(
                    [
                        (bloc["code"], bloc["name"])
                        for bloc in self.metadata.get_trading_bloc_list()
                    ]
                ),
            ),
            (
                "Countries",
                tuple(
                    (country["id"], country["name"])
                    for country in self.metadata.get_country_list()
                ),
            ),
        )
        context_data.update(
            {
                "select_options": locations,
            }
        )
        return context_data

    def get_initial(self):
        self.client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        self.current_user = self.client.users.get_current()
        trading_blocs = self.client.users.get(id=self.current_user.id).data["profile"][
            "trading_blocs"
        ]
        countries = self.client.users.get(id=self.current_user.id).data["profile"][
            "countries"
        ]
        return {
            "form": json.dumps(trading_blocs + countries),
        }

    def form_valid(self, form):
        locations = sorted(form.cleaned_data["form"])
        countries = []
        trading_blocs = []
        for location in locations:
            if self.metadata.is_trading_bloc_code(location):
                trading_blocs.append(location)
            else:
                countries.append(location)
        sorted_countries = sorted(countries)
        sorted_trading_blocs = sorted(trading_blocs)
        self.client.users.patch(
            id=str(self.current_user.id),
            profile={
                "id": str(self.current_user.id),
                "trading_blocs": sorted_trading_blocs,
                "countries": sorted_countries,
            },
        )
        return super().form_valid(form)


class UserEditGovernmentDepartment(UserEditBase):
    template_name = "users/account/edit_government_department.html"
    form_class = UserEditGovernmentDepartmentForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["government_departments"] = [
            (organisation_id, organisation_name)
            for organisation_id, organisation_name in self.metadata.get_gov_organisation_choices()
        ]
        return kwargs

    def form_valid(self, form):
        self.client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        self.current_user = self.client.users.get_current()
        self.client.profile.patch(
            id=str(self.current_user.id),
            organisations=form.cleaned_data["government_departments"],
        )
        return super().form_valid(form)
