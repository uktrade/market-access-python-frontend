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


class UserEditBase(FormView, TemplateView, MetadataMixin):

    def get_initial_ids(self, area, id_type="id"):
        self.client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        self.current_user = self.client.users.get_current()
        return [
            item[id_type]
            for item in self.client.profile.get(id=self.current_user.id).data[area]
        ]

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(
            {
                "page": "account",
            }
        )
        return context_data

    def patch_to_api(self, form, area):
        patch_args = {
            "id": str(self.current_user.id),
            area: sorted(form.cleaned_data["form"]),
        }
        self.client.profile.patch(**patch_args)

    def get_success_url(self):
        return reverse(
            "users:account",
        )


class UserEditPolicyTeams(UserEditBase):
    template_name = "users/account/edit_policy_teams.html"
    form_class = UserEditPolicyTeamsForm

    def get_initial(self):
        return {"form": self.get_initial_ids("policy_teams")}

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(
            {
                "select_options": [
                    (policy_team["id"], policy_team["title"])
                    for policy_team in self.metadata.get_policy_team_list()
                ]
            }
        )
        return context_data

    def form_valid(self, form):
        self.patch_to_api(form, "policy_teams")

        return super().form_valid(form)


class UserEditSectors(UserEditBase):
    template_name = "users/account/edit_sectors.html"
    form_class = UserEditSectorsForm

    def get_initial(self):
        return {"form": json.dumps(self.get_initial_ids("sectors"))}

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(
            {
                "select_options": [
                    (sector["id"], sector["name"])
                    for sector in self.metadata.get_sector_list(level=0)
                ]
            }
        )
        return context_data

    def form_valid(self, form):
        self.patch_to_api(form, "sectors")


class UserEditOverseasRegions(UserEditBase):
    template_name = "users/account/edit_overseas_regions.html"
    form_class = UserEditOverseasRegionsForm

    def get_initial(self):
        return {"form": json.dumps(self.get_initial_ids("overseas_regions"))}

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(
            {"select_options": self.metadata.get_overseas_region_choices()}
        )
        return context_data

    def form_valid(self, form):
        self.patch_to_api(form, "overseas_regions")
        return super().form_valid(form)


class UserEditBarrierLocations(UserEditBase):
    template_name = "users/account/edit_barrier_locations.html"
    form_class = UserEditBarrierLocationsForm

    def get_initial(self):
        trading_blocs = self.get_initial_ids("trading_blocs", "code")
        countries = self.get_initial_ids("countries")
        return {
            "form": json.dumps(trading_blocs + countries),
        }

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        locations = (
            (
                "Trading blocs",
                (
                    [
                        (bloc["code"], bloc["name"])
                        for bloc in self.metadata.get_trading_bloc_list()
                    ]
                ),
            ),
            (
                "Countries",
                (
                    [
                        (country["id"], country["name"])
                        for country in self.metadata.get_country_list()
                    ]
                ),
            ),
        )
        context_data.update({"select_options": locations})
        return context_data

    def form_valid(self, form):
        countries = []
        trading_blocs = []
        for location in form.cleaned_data["form"]:
            if self.metadata.is_trading_bloc_code(location):
                trading_blocs.append(location)
            else:
                countries.append(location)
        self.client.profile.patch(
            id=str(self.current_user.id),
            trading_blocs=sorted(trading_blocs),
            countries=sorted(countries),
        )
        return super().form_valid(form)


class UserEditGovernmentDepartment(UserEditBase):
    template_name = "users/account/edit_government_department.html"
    form_class = UserEditGovernmentDepartmentForm

    def get_form_kwargs(self):
        self.client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        self.current_user = self.client.users.get_current()
        kwargs = super().get_form_kwargs()
        kwargs["select_options"] = self.metadata.get_gov_organisation_choices()
        return kwargs

    def form_valid(self, form):
        self.patch_to_api(form, "organisations")
        return super().form_valid(form)
