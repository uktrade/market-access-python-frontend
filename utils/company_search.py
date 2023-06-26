from companies_house.api_client import CompaniesHouseAPIClient
from config.settings.base import COMPANIES_HOUSE_API_ENDPOINT, COMPANIES_HOUSE_API_KEY
from django.http import HttpResponse
from django.views.generic import View
from utils.exceptions import APIException

import logging
import json

logger = logging.getLogger(__name__)


class SearchCompany(View):
    def get(self, request, *args, **kwargs):
        error = None
        companies_house_api_client = CompaniesHouseAPIClient(
            api_key=COMPANIES_HOUSE_API_KEY, api_endpoint=COMPANIES_HOUSE_API_ENDPOINT
        )
        try:
            results = companies_house_api_client.search_companies(
                kwargs["search_term"], 100, True
            )
        except APIException:
            error = "There was an error finding the company"
            return error

        return HttpResponse(json.dumps(results["items"]))
