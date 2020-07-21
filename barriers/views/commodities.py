from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic import FormView, TemplateView

from .mixins import BarrierMixin
from barriers.forms.commodities import (
    CommodityLookupForm,
    MultiCommodityLookupForm,
    UpdateBarrierCommoditiesForm,
)
from utils.api.client import MarketAccessAPIClient


class BarrierEditCommodities(BarrierMixin, TemplateView):
    template_name = "barriers/edit/commodities.html"
    lookup_form_class = CommodityLookupForm
    update_form_class = UpdateBarrierCommoditiesForm

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return self.ajax(request, *args, **kwargs)

        lookup_form = self.lookup_form_class(
            data=request.GET.dict() or None,
            token=self.request.session.get("sso_token"),
        )
        if lookup_form.is_bound:
            lookup_form.full_clean()

        return self.render_to_response(self.get_context_data(lookup_form=lookup_form))

    def ajax(self, request, *args, **kwargs):
        lookup_form = MultiCommodityLookupForm(
            data=request.GET.dict() or None,
            token=self.request.session.get("sso_token"),
        )
        if lookup_form.is_valid():
            return JsonResponse({
                "status": "ok",
                "data": [commodity.to_dict() for commodity in lookup_form.commodities],
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": "Code not found",
            })

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["confirmed_commodities"] = self.get_confirmed_commodities()
        context_data["confirmed_commodities_data"] = [
            commodity.to_dict() for commodity in context_data["confirmed_commodities"]
        ]
        return context_data

    def add_confirmed_code(self, code):
        session_key = self.get_session_key()
        session_codes = self.request.session.get(session_key)
        if session_codes is None:
            session_codes = [commodity.code for commodity in self.barrier.commodities]
        session_codes.append(code)
        self.request.session[session_key] = list(set(session_codes))

    def clear_session_codes(self):
        session_key = self.get_session_key()
        try:
            del self.request.session[session_key]
            self.request.session.modified = True
        except KeyError:
            pass

    def get_confirmed_codes_from_session(self):
        session_key = self.get_session_key()
        return self.request.session.get(session_key)

    def get_confirmed_commodities(self):
        session_codes = self.get_confirmed_codes_from_session()

        if session_codes is None:
            return self.barrier.commodities
        if session_codes != []:
            client = MarketAccessAPIClient(self.request.session.get("sso_token"))
            return client.commodities.list(codes=",".join(session_codes))
        return []

    def remove_confirmed_code(self, code):
        session_key = self.get_session_key()
        session_codes = self.request.session.get(session_key)
        if session_codes is None:
            session_codes = [commodity.code for commodity in self.barrier.commodities]
        session_codes.remove(code)
        self.request.session[session_key] = session_codes

    def get_session_key(self):
        barrier_id = self.kwargs.get("barrier_id")
        return f"barrier:{barrier_id}:commodities"

    def post(self, request, *args, **kwargs):
        empty_form = self.lookup_form_class(token=self.request.session.get("sso_token"))

        if "confirm-commodity" in request.POST:
            code = request.POST.get("confirm-commodity")
            self.add_confirmed_code(code)
            return self.render_to_response(self.get_context_data(lookup_form=empty_form))
        elif "remove-commodity" in request.POST:
            code = request.POST.get("remove-commodity")
            self.remove_confirmed_code(code)
            return self.render_to_response(self.get_context_data(lookup_form=empty_form))
        elif request.POST.get("action") == "save":
            form = self.update_form_class(
                barrier_id=self.kwargs.get("barrier_id"),
                token=request.session.get("sso_token"),
                data=request.POST,
            )
            if form.is_valid():
                form.save()
                self.clear_session_codes()
                return HttpResponseRedirect(self.get_success_url())
            else:
                return self.form_invalid(form)

        elif request.POST.get("action") == "cancel":
            self.clear_session_codes()
            return HttpResponseRedirect(self.get_success_url())

        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
