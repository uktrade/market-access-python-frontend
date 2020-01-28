import logging
from json import JSONDecodeError
import requests

from django.conf import settings

from .resources import (
    BarriersResource,
    DocumentsResource,
    InteractionsResource,
    NotesResource,
    UsersResource,
    ReportsResource,
)
from utils.exceptions import APIException


logger = logging.getLogger(__name__)


class MarketAccessAPIClient:
    def __init__(self, token=None, **kwargs):
        self.token = token or settings.TRUSTED_USER_TOKEN
        self.barriers = BarriersResource(self)
        self.documents = DocumentsResource(self)
        self.interactions = InteractionsResource(self)
        self.notes = NotesResource(self)
        self.users = UsersResource(self)
        self.reports = ReportsResource(self)

    def request(self, method, path, **kwargs):
        url = f'{settings.MARKET_ACCESS_API_URI}{path}'
        headers = {
            'Authorization': f"Bearer {self.token}",
            'X-User-Agent': '',
            'X-Forwarded-For': '',
        }
        response = getattr(requests, method)(url, headers=headers, **kwargs)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise APIException(e)

        return response

    def get(self, path, json=True, **kwargs):
        response = self.request('get', path, **kwargs)
        if response.status_code is 200:
            if json:
                json_data = None
                try:
                    json_data = response.json()
                except JSONDecodeError:
                    # some endpoints might return 200 even if they failed (like /whoami as of 2020/01/06)
                    # in which case .json() is going to raise a JSONDecodeError
                    logging.error(
                        "Unexpected error at URI: %s, response.text: %s",
                        response.url,
                        response.text
                    )
                return json_data
            else:
                return response
        else:
            # TODO: The call has failed - investigate if sending back the error messages makes any sense?
            return None

    def post(self, path, **kwargs):
        return self.request_with_results('post', path, **kwargs)

    def patch(self, path, **kwargs):
        return self.request_with_results('patch', path, **kwargs)

    def put(self, path, **kwargs):
        return self.request_with_results('put', path, **kwargs)

    def delete(self, path, **kwargs):
        return self.request('delete', path, **kwargs)

    def request_with_results(self, method, path, **kwargs):
        response = self.request(method, path, **kwargs)
        return self.get_results_from_response_data(response.json())

    def get_results_from_response_data(self, response_data):
        if response_data.get('response', {}).get('success'):
            return response_data['response'].get(
                'result',
                response_data['response'].get('results')
            )
        else:
            return response_data
