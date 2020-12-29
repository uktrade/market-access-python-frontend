from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic import FormView

from .mixins import BarrierMixin
from barriers.constants import UK_COUNTRY_ID
from barriers.forms.commodities import (
    CommodityLookupForm,
    MultiCommodityLookupForm,
    UpdateBarrierCommoditiesForm,
)
from utils.api.client import MarketAccessAPIClient


class BarrierEditCommodities(BarrierMixin, FormView):
    template_name = "barriers/edit/commodities.html"
    lookup_form_class = CommodityLookupForm
    form_class = UpdateBarrierCommoditiesForm

    def get(self, request, *args, **kwargs):
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return self.ajax(request, *args, **kwargs)

        lookup_form = self.get_lookup_form()
        if lookup_form.is_bound:
            lookup_form.full_clean()

        return self.render_to_response(self.get_context_data(lookup_form=lookup_form))

    def ajax(self, request, *args, **kwargs):
        if request.GET.get("code"):
            form_class = CommodityLookupForm
        elif request.GET.get("codes"):
            form_class = MultiCommodityLookupForm
        else:
            return JsonResponse({"status": "error", "message": "Bad request"})

        lookup_form = self.get_lookup_form(form_class)
        if lookup_form.is_valid():
            return JsonResponse({
                "status": "ok",
                "data": lookup_form.get_commodity_data(),
            })
        else:
            return JsonResponse({"status": "error", "message": "HS commodity code not found"})

    def screen_reader_mode(self):
        # detect screen reader mode
        return "sr" == self.kwargs.get("mode", "")

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["confirmed_commodities"] = self.get_confirmed_commodities()
        context_data["confirmed_commodities_data"] = [
            commodity.to_dict() for commodity in context_data["confirmed_commodities"]
        ]
        context_data["screen_reader_mode"] = self.screen_reader_mode()
        return context_data

    def get_lookup_form(self, form_class=None):
        if form_class is None:
            form_class = CommodityLookupForm

        if self.barrier.country:
            initial = {"location": self.barrier.country["id"]}
        elif self.barrier.trading_bloc:
            initial = {"location": self.barrier.trading_bloc["code"]}

        return form_class(
            initial=initial,
            data=self.request.GET.dict() or None,
            token=self.request.session.get("sso_token"),
            locations=self.get_locations(),
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs

    def get_locations(self):
        if self.barrier.country:
            default_location = self.barrier.country
        elif self.barrier.trading_bloc:
            default_location = {
                "id": self.barrier.trading_bloc["code"],
                "name": self.barrier.trading_bloc["name"],
            }

        return (default_location, {"id": UK_COUNTRY_ID, "name": "United Kingdom"})

    def add_confirmed_commodity(self, code, location):
        session_key = self.get_session_key()
        session_commodities = self.get_session_commodities()
        existing_codes = [commodity["code"] for commodity in session_commodities]
        code = code.ljust(10, "0")

        if code not in existing_codes:
            session_commodities.append({"code": code, "location": location})
        self.request.session[session_key] = session_commodities

    def remove_confirmed_commodity(self, code):
        session_key = self.get_session_key()
        session_commodities = self.get_session_commodities()
        self.request.session[session_key] = [
            commodity for commodity in session_commodities if commodity["code"] != code
        ]

    def get_session_commodities(self):
        session_key = self.get_session_key()
        session_commodities = self.request.session.get(session_key)
        if session_commodities is None:
            session_commodities = []
            for commodity in self.barrier.commodities:
                if commodity.country:
                    session_commodities.append({"code": commodity.code, "location": commodity.country["id"]})
                elif commodity.trading_bloc:
                    session_commodities.append({"code": commodity.code, "location": commodity.trading_bloc["code"]})

            self.request.session[session_key] = session_commodities
        return session_commodities

    def clear_session_commodities(self):
        session_key = self.get_session_key()
        try:
            del self.request.session[session_key]
            self.request.session.modified = True
        except KeyError:
            pass

    def get_confirmed_commodities(self):
        session_key = self.get_session_key()
        session_commodities = self.request.session.get(session_key)

        if session_commodities is None:
            return self.barrier.commodities

        if session_commodities != []:
            client = MarketAccessAPIClient(self.request.session.get("sso_token"))
            hs6_session_codes = [
                commodity["code"][:6].ljust(10, "0") for commodity in session_commodities
            ]
            commodity_lookup = {
                commodity.code: commodity
                for commodity in client.commodities.list(codes=",".join(hs6_session_codes))
            }
            barrier_commodities = []
            for commodity_data in session_commodities:
                code = commodity_data.get("code")
                location = commodity_data.get("location")
                hs6_code = code[:6].ljust(10, "0")
                commodity = commodity_lookup.get(hs6_code)
                if commodity:
                    barrier_commodity = commodity.create_barrier_commodity(
                        code=code,
                        location=location,
                    )
                    barrier_commodities.append(barrier_commodity)
            return barrier_commodities

        return []

    def get_session_key(self):
        barrier_id = self.kwargs.get("barrier_id")
        return f"barrier:{barrier_id}:commodities"

    def post(self, request, *args, **kwargs):
        if "confirm-commodity" in request.POST:
            code = request.POST.get("code")
            location = request.POST.get("location")
            self.add_confirmed_commodity(code, location)
            return HttpResponseRedirect(self.request.path_info)
        elif "remove-commodity" in request.POST:
            code = request.POST.get("remove-commodity")
            self.remove_confirmed_commodity(code)
            return self.render_to_response(self.get_context_data(lookup_form=self.get_lookup_form()))
        elif request.POST.get("action") == "save":
            form = self.get_form()
            if form.is_valid():
                form.save()
                self.clear_session_commodities()
                return HttpResponseRedirect(self.get_success_url())
            else:
                return self.form_invalid(form)
        elif request.POST.get("action") == "cancel":
            self.clear_session_commodities()
            return HttpResponseRedirect(self.get_success_url())

        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
