import requests
from urllib.parse import quote_plus

from django.conf import settings

from users.exceptions import SSOException

from utils.exceptions import APIHttpException


class SSOClient:
    def __init__(self):
        # Cannot use the user's access token here as that is missing the introspection scope
        # webops team creates a user with the correct scope and a long lived token
        # that's what's being used here
        # if you find that this SSO_API_TOKEN does not work any longer reach out to webops team
        self.token = settings.SSO_API_TOKEN
        self.uri = settings.SSO_API_URI
        self.validate_client()

    def validate_client(self):
        if not self.uri:
            raise SSOException("SSO_API_URI is not set")
        if not self.token:
            raise SSOException("SSO_API_TOKEN is not set")

    def prepare_headers(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        return headers

    def get(self, path, **kwargs):
        url = f"{self.uri}{path}"
        headers = self.prepare_headers()
        response = requests.get(url=url, params=kwargs, headers=headers)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise APIHttpException(e)

        return response.json()

    def search_users(self, query):
        path = f"user/search/?autocomplete={quote_plus(query)}"
        response = self.get(path)
        users = response.get("results", [])
        return users
