import requests
import json

from django.conf import settings

from barriers.models import Company
from utils.exceptions import APIHttpException, DataHubException
from mohawk import Sender


class DatahubClient:
    def request(self, method, path, **kwargs):
        if not settings.DATAHUB_URL:
            raise DataHubException("DATAHUB_URL is not set")

        url = f'{settings.DATAHUB_URL}{path}'
        credentials = {
            "id": settings.DATAHUB_HAWK_ID,
            "key": settings.DATAHUB_HAWK_KEY,
            "algorithm": "sha256",
        }
        sender = Sender(
            credentials,
            url,
            method,
            content=json.dumps(kwargs),
            content_type="application/json",
            always_hash_content=False,
        )
        headers = {
            'Authorization': sender.request_header
        }
        response = getattr(requests, method)(
            url,
            verify=not settings.DEBUG,
            headers=headers,
            json=kwargs
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise APIHttpException(e)

        return response.json()

    def get(self, path, **kwargs):
        return self.request('get', path, **kwargs)

    def post(self, path, **kwargs):
        return self.request('post', path, **kwargs)

    def patch(self, path, **kwargs):
        return self.request('patch', path, **kwargs)

    def put(self, path, **kwargs):
        return self.request('put', path, **kwargs)

    def get_company(self, id):
        path = f'/v4/public/company/{id}'
        return Company(self.get(path))

    def search_company(self, query, page=1, limit=20, **kwargs):
        params = {
            'original_query': query,
            'offset': (page * limit) - limit,
            'limit': limit,
        }
        path = '/v4/public/search/company'
        data = self.post(path, **params)
        return {
            'count': data['count'],
            'results': [Company(company) for company in data['results']]
        }
