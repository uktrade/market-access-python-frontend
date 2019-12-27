import requests
from urllib.parse import quote_plus

from django.conf import settings

from users.exceptions import SSOException


class SSOClient:
    def request(self, method, path, **kwargs):
        if not settings.SSO_API_URI:
            raise SSOException("SSO_API_URI is not set")

        url = f'{settings.SSO_API_URI}{path}'

        response = getattr(requests, method)(url, json=kwargs)
        response.raise_for_status()
        return response.json()

    def search_users(self, query):
        path = f"user/search/?autocomplete={quote_plus(query)}"
        return self.request('get', path).get('results', [])
