import base64

import requests

from company_house.dataclasses import CompanyHouseCompany, CompanyHouseSearchResult
from config.settings.base import COMPANY_HOUSE_API_KEY


def get_company_from_id(company_id):
    """
    Get company house data from the API
    """
    url = "https://api.companieshouse.gov.uk/company/" + company_id
    headers = {
        "Authorization": "Basic "
        + base64.b64encode(COMPANY_HOUSE_API_KEY.encode()).decode(),
        "Host": "api.company-information.service.gov.uk",
    }
    response = requests.get(url, headers=headers)
    return CompanyHouseCompany(**response.json())


def search_companies(query, page=1, limit=20):
    """
    Search company house companies
    """
    url = "https://api.companieshouse.gov.uk/search/companies"
    headers = {
        "Authorization": "Basic "
        + base64.b64encode(COMPANY_HOUSE_API_KEY.encode()).decode(),
        "Host": "api.company-information.service.gov.uk",
    }
    params = {"q": query, "page": page, "limit": limit}
    response = requests.get(url, params=params, headers=headers)
    results = CompanyHouseSearchResult(**response.json())
    return results
