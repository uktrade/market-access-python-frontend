from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, View

from barriers.forms.location import (AddAdminAreaForm,
                                     EditCountryOrTradingBlocForm,
                                     EditLocationForm)
from utils.metadata import MetadataMixin

from .mixins import BarrierMixin


class BarrierEditLocation(MetadataMixin, BarrierMixin, FormView):
    template_name = "barriers/edit/location.html"
    form_class = EditLocationForm
    use_session_location = False

    def get(self, request, *args, **kwargs):
        if not self.use_session_location:
            if self.barrier.country:
                request.session["location"] = {
                    "country": self.barrier.country["id"],
                    "admin_areas": [admin_area["id"] for admin_area in self.barrier.admin_areas],
                }
            elif self.barrier.trading_bloc:
                request.session["location"] = {
                    "trading_bloc": self.barrier.trading_bloc["code"],
                }
            else:
                request.session["location"] = {
                    "country": None,
                    "admin_areas": [],
                }
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        country_id = self.request.session["location"].get("country")
        admin_area_ids = self.request.session["location"].get("admin_areas")
        trading_bloc_code = self.request.session["location"].get("trading_bloc")

        if country_id:
            context_data.update(
                {
                    "country": {
                        "id": country_id,
                        "name": self.metadata.get_country(country_id)["name"],
                    },
                    "admin_areas": self.metadata.get_admin_areas(admin_area_ids),
                }
            )
        elif trading_bloc_code:
            context_data["trading_bloc"] = self.metadata.get_trading_bloc(trading_bloc_code)
        return context_data

    def get_initial(self):
        return self.request.session.get("location", {})

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["countries"] = self.metadata.get_country_list()

        selected_country_id = self.request.session["location"].get("country")
        if selected_country_id:
            kwargs["admin_areas"] = self.metadata.get_admin_areas_by_country(selected_country_id)
            kwargs["trading_blocs"] = []
        else:
            kwargs["admin_areas"] = []
            kwargs["trading_blocs"] = self.metadata.get_trading_bloc_list()

        kwargs["barrier_id"] = str(self.kwargs.get("barrier_id"))
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs


class BarrierEditLocationSession(BarrierEditLocation):
    use_session_location = True


class BarrierEditCountryOrTradingBloc(MetadataMixin, BarrierMixin, FormView):
    template_name = "barriers/edit/country.html"
    form_class = EditCountryOrTradingBlocForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["countries"] = self.metadata.get_country_list()
        kwargs["trading_blocs"] = self.metadata.get_trading_bloc_list()
        return kwargs

    def get_initial(self):
        if self.request.session["location"].get("country"):
            return {"location": self.request.session["location"]["country"]}
        elif self.request.session["location"].get("trading_bloc"):
            return {"location": self.request.session["location"]["trading_bloc"]}

    def form_valid(self, form):
        location = self.request.session["location"]
        if (
            location.get("country") != form.cleaned_data["country"]
            or location.get("trading_bloc") != form.cleaned_data["trading_bloc"]
        ):
            self.request.session["location"] = {
                "country": form.cleaned_data["country"],
                "trading_bloc": form.cleaned_data["trading_bloc"],
                "admin_areas": [],
            }
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:edit_location_session",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class AddAdminArea(MetadataMixin, BarrierMixin, FormView):
    template_name = "barriers/edit/add_admin_area.html"
    form_class = AddAdminAreaForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        selected_country_id = self.request.session["location"]["country"]
        admin_areas = self.metadata.get_admin_areas_by_country(selected_country_id)
        admin_area_choices = [
            (admin_area["id"], admin_area["name"])
            for admin_area in admin_areas
            if admin_area["id"]
            not in self.request.session["location"].get("admin_areas", [])
        ]
        kwargs["admin_areas"] = admin_area_choices
        return kwargs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        admin_area_ids = self.request.session["location"].get("admin_areas", [])
        context_data.update({"admin_areas": self.metadata.get_admin_areas(admin_area_ids)})
        return context_data

    def form_valid(self, form):
        location = self.request.session["location"]
        location["admin_areas"].append(form.cleaned_data["admin_area"])
        self.request.session["location"] = location
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:edit_location_session",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class RemoveAdminArea(View):
    def post(self, request, *args, **kwargs):
        location = self.request.session["location"]
        admin_area = request.POST["admin_area"]
        location["admin_areas"].remove(admin_area)
        self.request.session["location"] = location
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "barriers:edit_location_session",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
