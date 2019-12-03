import requests

from django.conf import settings

from barriers.models import Barrier
from interactions.models import Interaction


class MarketAccessAPIClient:
    def __init__(self, token=None, **kwargs):
        self.barriers = BarriersResource(self)
        self.interactions = InteractionsResource(self)

        self._method = None
        self.token = token or settings.TRUSTED_USER_TOKEN
        self.use_cache = kwargs.get('use_cache', False)
        for k in kwargs:
            setattr(self, k, kwargs[k])

    def get(self, url, params=None, extra_headers=None, fields=None):
        url = self.get_url(url)

        params = params or {}
        if fields:
            params['fields'] = fields
        _headers = self.headers(extra_headers=extra_headers)
        response = requests.get(url, headers=_headers, params=params)
        response.raise_for_status()
        return response.json()

    def headers(self, extra_headers=None):
        _headers = {
            'Authorization': f'Token {self.token}',
            'X-User-Agent': '',
            'X-Forwarded-For': '',
        }
        if extra_headers and isinstance(extra_headers, dict):
            _headers.update(extra_headers)
        return _headers

    def get_url(self, path):
        """
        Construct a full API url
        """
        return f'{settings.API_URL}{path}'


class Resource:
    def __init__(self, client):
        self.client = client

    def list(self, **kwargs):
        return [
            self.model(result) for result in self.client.get(self.resource_name, params=kwargs)['results']
        ]

    def get(self, id, *args, **kwargs):
        url = f"{self.resource_name}/{id}"
        return self.model(self.client.get(url, *args, **kwargs))


class BarriersResource(Resource):
    resource_name = "barriers"
    model = Barrier


class InteractionsResource(Resource):
    resource_name = "interactions"
    model = Interaction
