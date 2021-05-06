from django.forms import Form
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView

from utils.metadata import MetadataMixin
from utils.sessions import SessionList

from ..forms.government_organisations import (
    AddGovernmentOrganisationsForm,
    EditGovernmentOrganisationsForm,
)
from .mixins import BarrierMixin


class BaseGovernmentOrganisationFormView(MetadataMixin, BarrierMixin, FormView):
    """
    View that helps to manage government organisations in the session
     - session key naming pattern: "<UUID>_government_organisations"
    """

    form_class = Form
    SESSION_KEY_POSTFIX = "government_organisations"
    barrier_id = None
    government_organisations = None

    @property
    def session_key(self):
        return f"{self.barrier_id}_{self.SESSION_KEY_POSTFIX}"

    def init_view(self, request, **kwargs):
        self.barrier_id = kwargs.get("barrier_id")
        self.government_organisations = SessionList(request.session, self.session_key)
        if request.session.get(self.session_key) is None:
            self.government_organisations.value = (
                self.barrier.government_organisation_ids_as_str
            )

    def get(self, request, *args, **kwargs):
        self.init_view(request, **kwargs)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.init_view(request, **kwargs)
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data[
            "selected_organisation"
        ] = self.metadata.get_gov_organisations_by_ids(
            self.government_organisations.value
        )
        return context_data


class BarrierEditGovernmentOrganisations(BaseGovernmentOrganisationFormView):
    template_name = "barriers/edit/government_organisations.html"
    form_class = EditGovernmentOrganisationsForm

    def get_initial(self):
        return {
            "organisations": self.government_organisations.value,
        }

    def form_valid(self, form):
        form.save()
        self.request.session.pop(self.government_organisations.key)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:public_barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organisations"] = self.metadata.get_gov_organisation_choices()
        kwargs["barrier_id"] = str(self.barrier_id)
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs


class BarrierAddGovernmentOrganisation(BaseGovernmentOrganisationFormView):
    template_name = "barriers/edit/add_government_organisation.html"
    form_class = AddGovernmentOrganisationsForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["organisations"] = [
            (organisation_id, organisation_name)
            for organisation_id, organisation_name in self.metadata.get_gov_organisation_choices()
            if str(organisation_id) not in self.government_organisations.value
        ]
        return kwargs

    def form_valid(self, form):
        self.government_organisations.append(form.cleaned_data["organisation"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:edit_gov_orgs",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class BarrierRemoveGovernmentOrganisation(BaseGovernmentOrganisationFormView):
    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        organisation = request.POST.get("organisation")
        self.government_organisations.remove(str(organisation))
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "barriers:edit_gov_orgs",
            kwargs={"barrier_id": self.barrier_id},
        )
