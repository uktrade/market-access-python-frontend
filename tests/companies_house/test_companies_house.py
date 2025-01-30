import json
from unittest import mock

import pytest
from django.conf import settings

from barriers.forms.companies import EditCompaniesForm
from companies_house.api_client import CompaniesHouseAPIClient
from companies_house.dataclasses import (
    CompanyHouseCompany,
    CompanyHouseSearchResult,
    CompanyHouseSearchResultItem,
)
from core.filecache import memfiles
from core.tests import MarketAccessTestCase


class CompaniesHouseTestCase(MarketAccessTestCase):

    mock_form = EditCompaniesForm()
    mock_form.api_key = "An API Key"  # pragma: allowlist secret

    def get_company_mocked_requests_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        def get_company_from_id_results():
            # Search Result Test Case List:
            # self.get_company_results[0] -> COMPANY WITH FULL DETAILS
            # self.get_company_results[1] -> COMPANY MISSING REQUIRED FIELD
            # self.get_company_results[2] -> COMPANY WITH REQUIRED DETAILS
            file = (
                f"{settings.BASE_DIR}/../tests/companies_house/fixtures/companies.json"
            )
            get_company_results = json.loads(memfiles.open(file))
            return get_company_results

        if args[0] == "success_test_endpoint/company/1":
            return MockResponse(
                get_company_from_id_results()[0],
                200,
            )
        elif args[0] == "missing_field_test_endpoint/company/1":
            return MockResponse(
                get_company_from_id_results()[1],
                200,
            )
        elif args[0] == "required_fields_only_test_endpoint/company/1":
            return MockResponse(
                get_company_from_id_results()[2],
                200,
            )

    def search_mocked_requests_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        def get_companies_search_results():
            # Search Result Test Case List:
            # self.companies_search_results[0] -> COMPANY WITH FULL DETAILS
            # self.companies_search_results[1] -> COMPANY WITH MISSING FIELDS
            # self.companies_search_results[2] -> COMPANY WITH INCORRECT FORMATTING
            # self.companies_search_results[3] -> COMPANY WITH EXTRA FIELD
            # self.companies_search_results[4] -> COMPANY WITH INCORRECT SUBTYPE
            # self.companies_search_results[5] -> COMPANY WITH REQUIRED DETAILS
            file = f"{settings.BASE_DIR}/../tests/companies_house/fixtures/companies_search_data.json"
            companies_search_results = json.loads(memfiles.open(file))
            return companies_search_results

        # Based on the URL received, return different search result from fixture
        if args[0] == "success_test_endpoint/search/companies":
            return MockResponse(
                {
                    "total_results": 1,
                    "items_per_page": 100,
                    "page_number": 1,
                    "start_index": 0,
                    "kind": "search#companies",
                    "items": [get_companies_search_results()[0]],
                },
                200,
            )
        elif args[0] == "missing_field_test_endpoint/search/companies":
            return MockResponse(
                {
                    "total_results": 2,
                    "items_per_page": 100,
                    "page_number": 1,
                    "start_index": 0,
                    "kind": "search#companies",
                    "items": [
                        get_companies_search_results()[0],
                        get_companies_search_results()[1],
                    ],
                },
                200,
            )
        elif args[0] == "fields_incorrectly_formatted_endpoint/search/companies":
            return MockResponse(
                {
                    "total_results": 2,
                    "items_per_page": 100,
                    "page_number": 1,
                    "start_index": 0,
                    "kind": "search#companies",
                    "items": [
                        get_companies_search_results()[0],
                        get_companies_search_results()[2],
                    ],
                },
                200,
            )
        elif args[0] == "extra_field_endpoint/search/companies":
            return MockResponse(
                {
                    "total_results": 2,
                    "items_per_page": 100,
                    "page_number": 1,
                    "start_index": 0,
                    "kind": "search#companies",
                    "items": [
                        get_companies_search_results()[0],
                        get_companies_search_results()[3],
                    ],
                },
                200,
            )
        elif args[0] == "incorrect_subtype_endpoint/search/companies":
            return MockResponse(
                {
                    "total_results": 2,
                    "items_per_page": 100,
                    "page_number": 1,
                    "start_index": 0,
                    "kind": "search#companies",
                    "items": [
                        get_companies_search_results()[0],
                        get_companies_search_results()[4],
                    ],
                },
                200,
            )
        elif args[0] == "required_fields_test_endpoint/search/companies":
            return MockResponse(
                {
                    "total_results": 1,
                    "items_per_page": 100,
                    "page_number": 1,
                    "start_index": 0,
                    "kind": "search#companies",
                    "items": [
                        get_companies_search_results()[5],
                    ],
                },
                200,
            )

        return MockResponse(None, 404)

    @mock.patch("requests.get", side_effect=search_mocked_requests_get)
    def test_get_successful_search_result(self, mock_get):
        """
        Check a successful search returns a company search result with full details
        """
        self.mock_form.api_endpoint = "success_test_endpoint"

        result = CompaniesHouseAPIClient.search_companies(self.mock_form, 100)

        assert type(result) is CompanyHouseSearchResult
        assert result.total_results == 1

        result_item = result.items[0]
        assert len(result.items) == 1
        assert type(result_item) is CompanyHouseSearchResultItem
        assert result_item.title == "COMPANY WITH FULL DETAILS"

    @mock.patch("requests.get", side_effect=search_mocked_requests_get)
    @mock.patch("sentry_sdk.capture_message")
    def test_get_search_result_missing_required_fields(self, mock_alert, mock_get):
        """
        Check a successful search avoids returning a company missing required fields
        """
        self.mock_form.api_endpoint = "missing_field_test_endpoint"

        result = CompaniesHouseAPIClient.search_companies(self.mock_form, 100)

        assert type(result) is CompanyHouseSearchResult
        assert result.total_results == 2

        assert mock_alert.call_count == 1
        assert "Problem detected with companies house data" in str(mock_alert.call_args)
        assert "missing 1 required positional argument: 'company_number'" in str(
            mock_alert.call_args
        )

        # Ensure the items with correct details are still returned
        result_item = result.items[0]
        assert len(result.items) == 1
        assert type(result_item) is CompanyHouseSearchResultItem
        assert result_item.title == "COMPANY WITH FULL DETAILS"

    @mock.patch("requests.get", side_effect=search_mocked_requests_get)
    @mock.patch("sentry_sdk.capture_message")
    def test_get_search_result_fields_incorrectly_formatted(self, mock_alert, mock_get):
        """
        Check a successful search avoids returning a company with incorrect field formats
        """
        self.mock_form.api_endpoint = "fields_incorrectly_formatted_endpoint"

        result = CompaniesHouseAPIClient.search_companies(self.mock_form, 100)

        assert type(result) is CompanyHouseSearchResult
        assert result.total_results == 2

        assert mock_alert.call_count == 1
        assert "Problem detected with companies house data" in str(mock_alert.call_args)
        assert "time data 'broken formatting' does not match format '%Y-%m-%d'" in str(
            mock_alert.call_args
        )

        # Ensure the items with correct details are still returned
        result_item = result.items[0]
        assert len(result.items) == 1
        assert type(result_item) is CompanyHouseSearchResultItem
        assert result_item.title == "COMPANY WITH FULL DETAILS"

    @mock.patch("requests.get", side_effect=search_mocked_requests_get)
    @mock.patch("sentry_sdk.capture_message")
    def test_get_search_result_extra_field(self, mock_alert, mock_get):
        """
        Check a successful search avoids returning a company with extra, unidentified fields
        """
        self.mock_form.api_endpoint = "extra_field_endpoint"

        result = CompaniesHouseAPIClient.search_companies(self.mock_form, 100)

        assert type(result) is CompanyHouseSearchResult
        assert result.total_results == 2

        assert mock_alert.call_count == 1
        assert "Problem detected with companies house data" in str(mock_alert.call_args)
        assert "__init__() got an unexpected keyword argument 'sector'" in str(
            mock_alert.call_args
        )

        # Ensure the items with correct details are still returned
        result_item = result.items[0]
        assert len(result.items) == 1
        assert type(result_item) is CompanyHouseSearchResultItem
        assert result_item.title == "COMPANY WITH FULL DETAILS"

    @mock.patch("requests.get", side_effect=search_mocked_requests_get)
    @mock.patch("sentry_sdk.capture_message")
    def test_get_search_result_incorrect_subtype(self, mock_alert, mock_get):
        """
        Check a successful search avoids returning a company with incorrect sub-object (address)
        """
        self.mock_form.api_endpoint = "incorrect_subtype_endpoint"

        result = CompaniesHouseAPIClient.search_companies(self.mock_form, 100)

        assert type(result) is CompanyHouseSearchResult
        assert result.total_results == 2

        assert mock_alert.call_count == 1
        assert "Problem detected with companies house data" in str(mock_alert.call_args)
        assert "argument after ** must be a mapping, not str" in str(
            mock_alert.call_args
        )

        # Ensure the items with correct details are still returned
        result_item = result.items[0]
        assert len(result.items) == 1
        assert type(result_item) is CompanyHouseSearchResultItem
        assert result_item.title == "COMPANY WITH FULL DETAILS"

    @mock.patch("requests.get", side_effect=search_mocked_requests_get)
    def test_get_successful_search_result_required_fields_only(self, mock_get):
        """
        Check a successful search returns a company search result with required details
        """
        self.mock_form.api_endpoint = "required_fields_test_endpoint"

        result = CompaniesHouseAPIClient.search_companies(self.mock_form, 100)

        assert type(result) is CompanyHouseSearchResult
        assert result.total_results == 1

        result_item = result.items[0]
        assert len(result.items) == 1
        assert type(result_item) is CompanyHouseSearchResultItem
        assert result_item.title == "COMPANY WITH REQUIRED DETAILS"

    @mock.patch("requests.get", side_effect=get_company_mocked_requests_get)
    def test_get_company_success(self, mock_get):
        """
        Check a successful response for the get company request
        """

        client_obj = CompaniesHouseAPIClient(
            api_endpoint="success_test_endpoint",
            api_key="An API Key",  # pragma: allowlist secret
        )

        result = client_obj.get_company_from_id("1")

        assert type(result) is CompanyHouseCompany
        assert result.company_name == "FULL DETAILS"

    @mock.patch("requests.get", side_effect=get_company_mocked_requests_get)
    def test_get_company_missing_field(self, mock_get):
        """
        Check a error triggeres for the company missing required field
        """

        client_obj = CompaniesHouseAPIClient(
            api_endpoint="missing_field_test_endpoint",
            api_key="An API Key",  # pragma: allowlist secret
        )

        with pytest.raises(Exception) as error_triggered:
            client_obj.get_company_from_id("1")

        assert (
            "__init__() missing 1 required positional argument: 'company_number'"
            in str(error_triggered)
        )

    @mock.patch("requests.get", side_effect=get_company_mocked_requests_get)
    def test_get_company_required_fields_only(self, mock_get):
        """
        Check a successful response for companies missing optional fields
        """

        client_obj = CompaniesHouseAPIClient(
            api_endpoint="required_fields_only_test_endpoint",
            api_key="An API Key",  # pragma: allowlist secret
        )

        result = client_obj.get_company_from_id("1")

        assert type(result) is CompanyHouseCompany
        assert result.company_name == "CRUCIAL DETAILS"
