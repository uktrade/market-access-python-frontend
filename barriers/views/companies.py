import json
import logging

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView, View

from barriers.forms.companies import (
    AddCompanyForm,
    CompanySearchForm,
    EditCompaniesForm,
)
from companies_house.api_client import CompaniesHouseAPIClient
from config.settings.base import COMPANIES_HOUSE_API_ENDPOINT, COMPANIES_HOUSE_API_KEY
from utils.exceptions import APIException

from .mixins import BarrierMixin

logger = logging.getLogger(__name__)


class BarrierSearchCompany(BarrierMixin, FormView):
    template_name = "barriers/companies/search.html"
    form_class = CompanySearchForm

    def form_valid(self, form):
        error = None
        companies_house_api_client = CompaniesHouseAPIClient(
            api_key=COMPANIES_HOUSE_API_KEY, api_endpoint=COMPANIES_HOUSE_API_ENDPOINT
        )
        try:
            results = companies_house_api_client.search_companies(
                form.cleaned_data["query"], 100
            )
        except APIException:
            error = "There was an error finding the company"
            results = []

        return self.render_to_response(
            self.get_context_data(form=form, results=results, error=error)
        )


class CompanyDetail(BarrierMixin, FormView):
    template_name = "barriers/companies/detail.html"
    form_class = AddCompanyForm

    def get_context_data(self, **kwargs):
        companies_house_api_client = CompaniesHouseAPIClient(
            api_key=COMPANIES_HOUSE_API_KEY, api_endpoint=COMPANIES_HOUSE_API_ENDPOINT
        )
        context_data = super().get_context_data(**kwargs)
        company_id = str(self.kwargs.get("company_id"))
        context_data["company"] = companies_house_api_client.get_company_from_id(
            company_id
        )
        return context_data

    def form_valid(self, form):
        companies_house_api_client = CompaniesHouseAPIClient(
            api_key=COMPANIES_HOUSE_API_KEY, api_endpoint=COMPANIES_HOUSE_API_ENDPOINT
        )
        company = companies_house_api_client.get_company_from_id(
            form.cleaned_data["company_id"]
        )
        companies = self.request.session.get("companies", [])
        companies.append(
            {
                "id": company.id,
                "source": "company_house",
                "name": company.company_name,
                "address": company.address_display,
            }
        )
        self.request.session["companies"] = companies
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:edit_companies_session",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class BarrierEditCompanies(BarrierMixin, FormView):
    template_name = "barriers/companies/edit.html"
    form_class = EditCompaniesForm
    use_session_companies = False

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        # Build JSON with fields matching companies house keys
        companies_context_list = []
        for company in self.barrier.companies:
            companies_context_list.append(
                {
                    "company_number": company["id"],
                    "title": company["name"],
                }
            )

        related_organisations_context_list = []
        for related_organisation in self.barrier.related_organisations:
            related_organisations_context_list.append(related_organisation["name"])

        context_data["companies_affected"] = json.dumps(companies_context_list)
        context_data["unrecognised_company"] = json.dumps(
            related_organisations_context_list
        )
        return context_data

    def form_valid(self, form):
        form.save(self.barrier.id, self.request.session.get("sso_token"))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


class BarrierEditCompaniesSession(BarrierEditCompanies):
    use_session_companies = True


class BarrierRemoveCompany(View):
    """
    Remove the company from the session and redirect
    """

    def post(self, request, *args, **kwargs):
        companies = self.request.session.get("companies", [])
        company_id = request.POST.get("company_id")

        self.request.session["companies"] = [
            company for company in companies if company_id != company["id"]
        ]
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse(
            "barriers:edit_companies_session",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
