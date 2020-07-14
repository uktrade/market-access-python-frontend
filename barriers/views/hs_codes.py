from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView

from .mixins import BarrierMixin
from barriers.forms.hs_codes import UpdateBarrierHSCodesForm

from utils.api.client import MarketAccessAPIClient


class BarrierEditHSCodes(BarrierMixin, FormView):
    template_name = "barriers/edit/hs_codes.html"
    form_class = UpdateBarrierHSCodesForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["confirmed_hs_codes"] = self.get_confirmed_hs_codes()
        return context_data

    def form_valid(self, form):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        code = form.cleaned_data.get("code")
        hs_code = client.hs_codes.get(id=code)
        return self.render_to_response(self.get_context_data(form=form, hs_code=hs_code))

    def add_confirmed_code(self, code):
        session_key = self.get_session_key()
        session_codes = self.request.session.get(session_key)
        if session_codes is None:
            session_codes = [hs_code.code for hs_code in self.barrier.hs_codes]
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

    def get_confirmed_hs_codes(self):
        session_codes = self.get_confirmed_codes_from_session()

        if session_codes is None:
            return self.barrier.hs_codes
        if session_codes != []:
            client = MarketAccessAPIClient(self.request.session.get("sso_token"))
            return client.hs_codes.list(codes=",".join(session_codes))
        return []

    def remove_confirmed_code(self, code):
        session_key = self.get_session_key()
        session_codes = self.request.session.get(session_key)
        if session_codes is None:
            session_codes = [hs_code.code for hs_code in self.barrier.hs_codes]
        session_codes.remove(code)
        self.request.session[session_key] = session_codes

    def get_session_key(self):
        barrier_id = self.kwargs.get("barrier_id")
        return f"barrier:{barrier_id}:hs_codes"

    def post(self, request, *args, **kwargs):
        empty_form = UpdateBarrierHSCodesForm()

        if "confirm-hs-code" in request.POST:
            code = request.POST.get("confirm-hs-code")
            self.add_confirmed_code(code)
            return self.render_to_response(self.get_context_data(form=empty_form))
        elif "remove-hs-code" in request.POST:
            code = request.POST.get("remove-hs-code")
            self.remove_confirmed_code(code)
            return self.render_to_response(self.get_context_data(form=empty_form))
        elif request.POST.get("action") == "save":
            client = MarketAccessAPIClient(self.request.session.get("sso_token"))
            codes = self.get_confirmed_codes_from_session()
            hs_codes = [{"code": code} for code in codes]
            barrier_id = self.kwargs.get("barrier_id")
            client.barriers.patch(id=barrier_id, hs_codes=hs_codes)
            self.clear_session_codes()
            return HttpResponseRedirect(self.get_success_url())
        elif request.POST.get("action") == "cancel":
            self.clear_session_codes()
            return HttpResponseRedirect(self.get_success_url())

        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
