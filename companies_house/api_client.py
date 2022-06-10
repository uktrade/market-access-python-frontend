import base64

import requests

from companies_house.dataclasses import CompanyHouseCompany, CompanyHouseSearchResult


class CompaniesHouseAPIClient(object):
    api_key: str

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_company_from_id(self, company_id):
        """
        Get company house data from the API
        """
        url = "https://api.companieshouse.gov.uk/company/" + company_id
        headers = {
            "Authorization": "Basic "
            + base64.b64encode(self.api_key.encode()).decode(),
            "Host": "api.company-information.service.gov.uk",
        }
        response = requests.get(url, headers=headers)
        return CompanyHouseCompany(**response.json())

    def search_companies(self, query, page=1, limit=20):
        """
        Search company house companies
        """
        url = "https://api.companieshouse.gov.uk/search/companies"
        headers = {
            "Authorization": "Basic "
            + base64.b64encode(self.api_key.encode()).decode(),
            "Host": "api.company-information.service.gov.uk",
        }
        params = {"q": query, "page": page, "limit": limit}
        response = requests.get(url, params=params, headers=headers)
        results = CompanyHouseSearchResult(**response.json())
        return results
