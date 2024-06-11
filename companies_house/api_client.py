import base64
import logging

import requests

from companies_house.dataclasses import CompanyHouseCompany, CompanyHouseSearchResult

logger = logging.getLogger(__name__)

DEFAULT_API_ENDPOINT = "https://api.companieshouse.gov.uk"


class CompaniesHouseAPIClient(object):
    api_key: str

    def __init__(self, api_key: str, api_endpoint: str = DEFAULT_API_ENDPOINT):
        self.api_key = api_key
        self.api_endpoint = api_endpoint

    def get_company_from_id(self, company_id: str):
        """
        Get company house data from the API
        """
        url = f"{self.api_endpoint}/company/{company_id}"
        headers = {
            "Authorization": "Basic " + base64.b64encode(self.api_key.encode()).decode()
        }
        response = requests.get(url, headers=headers)
        return CompanyHouseCompany(**response.json())

    def search_companies(self, query: str, limit: int = 100, raw_json: bool = False):
        """
        Search company house companies
        """
        url = f"{self.api_endpoint}/search/companies"
        headers = {
            "Authorization": "Basic " + base64.b64encode(self.api_key.encode()).decode()
        }
        params = {"q": query, "items_per_page": limit}

        response = requests.get(url, params=params, headers=headers)

        if raw_json is True:
            return response.json()
        else:
            return CompanyHouseSearchResult(**response.json())
