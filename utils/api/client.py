import logging
from json import JSONDecodeError
import requests

from django.conf import settings

from .resources import (
    BarriersResource,
    DocumentsResource,
    NotesResource,
    UsersResource,
    ReportsResource,
)
from utils.exceptions import APIHttpException, APIJsonException


logger = logging.getLogger(__name__)


class MarketAccessAPIClient:
    def __init__(self, token=None, **kwargs):
        self.token = token or settings.TRUSTED_USER_TOKEN
        self.barriers = BarriersResource(self)
        self.documents = DocumentsResource(self)
        self.notes = NotesResource(self)
        self.users = UsersResource(self)
        self.reports = ReportsResource(self)

    def request(self, method, path, **kwargs):
        url = f"{settings.MARKET_ACCESS_API_URI}{path}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "X-User-Agent": "",
            "X-Forwarded-For": "",
        }
        response = getattr(requests, method)(url, headers=headers, **kwargs)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            logger.error(e)
            raise APIHttpException(e)

        return response

    def get(self, path, raw=False, **kwargs):
        response = self.request("get", path, **kwargs)

        if raw:
            return response

        try:
            return response.json()
        except JSONDecodeError:
            raise APIJsonException(
                f"Non json response at '{response.url}'. "
                f"Response text: {response.text}"
            )

    def post(self, path, **kwargs):
        return self.request_with_results("post", path, **kwargs)

    def patch(self, path, **kwargs):
        return self.request_with_results("patch", path, **kwargs)

    def put(self, path, **kwargs):
        return self.request_with_results("put", path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request("delete", path, **kwargs)

    def request_with_results(self, method, path, **kwargs):
        response = self.request(method, path, **kwargs)
        return self.get_results_from_response_data(response.json())

    def get_results_from_response_data(self, response_data):
        if response_data.get("response", {}).get("success"):
            return response_data["response"].get(
                "result", response_data["response"].get("results")
            )
        else:
            return response_data
