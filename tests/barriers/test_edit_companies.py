import logging
from http import HTTPStatus

from django.urls import reverse
from mock import patch

from companies_house.dataclasses import CompanyHouseCompany, CompanyHouseSearchResult
from core.tests import MarketAccessTestCase

logger = logging.getLogger(__name__)


class EditCompaniesTestCase(MarketAccessTestCase):
    company_id = "04301762"
    company_name = "TEST LIMITED"
    company_data = {
        "accounts": {
            "last_accounts": {
                "made_up_to": "2012-03-30",
                "type": "dormant",
                "period_end_on": "2012-03-30",
            },
            "accounting_reference_date": {"month": "03", "day": "30"},
        },
        "company_status": "active",
        "company_name": company_name,
        "company_number": company_id,
        "date_of_creation": "2001-10-09",
        "has_charges": False,
        "has_insolvency_history": False,
        "jurisdiction": "england-wales",
        "last_full_members_list_date": "2012-10-09",
        "links": {},
        "previous_company_names": [],
        "registered_office_address": {
            "address_line_2": "Garstang",
            "address_line_1": "The Resource Centre Bridge Street",
            "region": "Lancashire",
            "locality": "Preston",
            "postal_code": "PR3 1YB",
        },
        "sic_codes": ["82990"],
        "type": "ltd",
        "undeliverable_registered_office_address": False,
    }

    def test_edit_companies_landing_page(self):
        """
        Landing page should have the barrier's companies in the form
        """
        response = self.client.get(
            reverse(
                "barriers:edit_companies", kwargs={"barrier_id": self.barrier["id"]}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        company_ids = [company["id"] for company in self.barrier["companies"]]
        for id in company_ids:
            assert str(id) in response.context_data["companies_affected"]

    def test_company_search_page_loads(self):
        """
        The search page should load with a form in the context
        """
        response = self.client.get(
            reverse(
                "barriers:search_company", kwargs={"barrier_id": self.barrier["id"]}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context

    @patch("barriers.views.companies.CompaniesHouseAPIClient.search_companies")
    def test_company_search_submit(self, mock_post):
        """
        Searching should call the Datahub API
        """
        mock_post.return_value = CompanyHouseSearchResult(
            items_per_page=10,
            total_results=1,
            items=[
                {
                    "title": self.company_data["company_name"],
                    "description": "",
                    "kind": "company",
                    "address": self.company_data["registered_office_address"],
                    "address_snippet": "",
                    "company_number": self.company_data["company_number"],
                    "company_type": self.company_data["type"],
                    "description_identifier": [],
                    "company_status": self.company_data["company_status"],
                    "matches": {},
                    "links": self.company_data["links"],
                    "snippet": "",
                    "date_of_creation": self.company_data["date_of_creation"],
                }
            ],
            page_number=1,
            start_index=0,
            kind="search_results",
        )
        response = self.client.post(
            reverse(
                "barriers:search_company", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"query": "test search"},
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        assert "results" in response.context
        results = response.context["results"]
        assert results.total_results == 1
        assert results.items[0].id == self.company_id
        assert results.items[0].name == self.company_name

    @patch("barriers.views.companies.CompaniesHouseAPIClient.get_company_from_id")
    def test_company_detail(self, mock_get_company):
        """
        Company Detail should call the Datahub API
        """
        mock_get_company.return_value = CompanyHouseCompany(**self.company_data)
        response = self.client.get(
            reverse(
                "barriers:company_detail",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "company_id": self.company_id,
                },
            ),
        )
        assert response.status_code == HTTPStatus.OK
        mock_get_company.assert_called_with(self.company_id)
        assert response.context["company"].id == self.company_id
        assert response.context["company"].name == self.company_name

    @patch("utils.api.resources.APIResource.patch")
    @patch("barriers.views.companies.CompaniesHouseAPIClient.get_company_from_id")
    def test_add_company(self, mock_get_company, mock_patch):
        """
        Add company should change the session, not call the API
        """
        mock_company_data = CompanyHouseCompany(**self.company_data)
        mock_get_company.return_value = mock_company_data
        response = self.client.post(
            reverse(
                "barriers:company_detail",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "company_id": self.company_id,
                },
            ),
            data={"company_id": self.company_id},
        )
        assert response.status_code == HTTPStatus.FOUND
        new_company = {
            "id": self.company_id,
            "name": self.company_name,
            "source": "company_house",
            "address": mock_company_data.address_display,
        }
        assert new_company in self.client.session["companies"]
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_remove_company(self, mock_patch):
        """
        Removing a company should remove it from the session, not call the API
        """
        companies = [
            {
                "id": self.company_id,
                "name": self.company_name,
            },
            {
                "id": self.barrier["companies"][0]["id"],
                "name": self.barrier["companies"][0]["name"],
            },
        ]
        self.update_session({"companies": companies})

        response = self.client.post(
            reverse(
                "barriers:remove_company", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"company_id": self.company_id},
        )
        assert response.status_code == HTTPStatus.FOUND
        companies = self.client.session["companies"]
        assert {
            "id": self.company_id,
            "name": self.company_name,
        } not in self.client.session["companies"]
        assert self.barrier["companies"][0] in self.client.session["companies"]
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_confirm_companies(self, mock_patch):
        companies_entry = (
            '[{"company_number":"000011111","title":"company_name_goes_here"}]'
        )

        response = self.client.post(
            reverse(
                "barriers:edit_companies",
                kwargs={
                    "barrier_id": self.barrier["id"],
                },
            ),
            data={"companies_affected": companies_entry, "unrecognised_company": []},
        )

        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            companies=[
                {
                    "id": "000011111",
                    "name": "company_name_goes_here",
                }
            ],
            related_organisations=[],
        )
        assert "companies" not in self.client.session
