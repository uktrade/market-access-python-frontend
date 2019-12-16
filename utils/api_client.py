import requests

from django.conf import settings

from barriers.models import Barrier
from interactions.models import HistoryItem, Interaction


class MarketAccessAPIClient:
    def __init__(self, token=None, **kwargs):
        self.token = token or settings.TRUSTED_USER_TOKEN
        self.barriers = BarriersResource(self)
        self.interactions = InteractionsResource(self)
        self.notes = NotesResource(self)

    def request(self, method, path, **kwargs):
        url = f'{settings.MARKET_ACCESS_API_URI}{path}'
        headers = {
            'Authorization': "Bearer {self.token}",
            'X-User-Agent': '',
            'X-Forwarded-For': '',
        }
        response = getattr(requests, method)(url, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def get(self, path, **kwargs):
        return self.request('get', path, **kwargs)

    def post(self, path, **kwargs):
        return self.request_with_results('post', path, **kwargs)

    def patch(self, path, **kwargs):
        return self.request_with_results('patch', path, **kwargs)

    def put(self, path, **kwargs):
        return self.request_with_results('put', path, **kwargs)

    def request_with_results(self, method, path, **kwargs):
        try:
            response_data = self.request(method, path, **kwargs)
            return self.get_results_from_response_data(response_data)
        except requests.exceptions.HTTPError as http_exception:
            raise APIException(http_exception)

    def get_results_from_response_data(self, response_data):
        if response_data.get('response', {}).get('success'):
            return response_data['response'].get(
                'result',
                response_data['response'].get('results')
            )
        else:
            return response_data


class Resource:
    def __init__(self, client):
        self.client = client

    def list(self, **kwargs):
        return [
            self.model(result)
            for result in self.client.get(
                self.resource_name,
                params=kwargs
            )['results']
        ]

    def get(self, id, *args, **kwargs):
        url = f"{self.resource_name}/{id}"
        return self.model(self.client.get(url, *args, **kwargs))

    def patch(self, id, *args, **kwargs):
        url = f"{self.resource_name}/{id}"
        return self.model(self.client.patch(url, json=kwargs))

    def create(self, *args, **kwargs):
        return self.model(self.client.post(self.resource_name, data=kwargs))

    def update(self, id, *args, **kwargs):
        url = f"{self.resource_name}/{id}"
        return self.model(self.client.put(url, data=kwargs))


class BarriersResource(Resource):
    resource_name = "barriers"
    model = Barrier

    def get_history(self, barrier_id, **kwargs):
        url = f"barriers/{barrier_id}/history"
        return [
            HistoryItem(result)
            for result in self.client.get(url, params=kwargs)['history']
        ]

    def get_assessment_history(self, barrier_id, **kwargs):
        url = f"barriers/{barrier_id}/assessment_history"
        return [
            HistoryItem(result)
            for result in self.client.get(url, params=kwargs)['history']
        ]


class InteractionsResource(Resource):
    resource_name = "interactions"
    model = Interaction

    def list(self, barrier_id, **kwargs):
        url = f"barriers/{barrier_id}/interactions"
        return [
            self.model(result)
            for result in self.client.get(url, params=kwargs)['results']
        ]


class NotesResource(Resource):
    resource_name = "notes"
    model = Interaction

    def create(self, barrier_id, *args, **kwargs):
        url = f"barriers/{barrier_id}/interactions"
        return self.model(self.client.post(url, data=kwargs))

    def update(self, id, *args, **kwargs):
        url = f"barriers/interactions/{id}"
        return self.model(self.client.patch(url, data=kwargs))
