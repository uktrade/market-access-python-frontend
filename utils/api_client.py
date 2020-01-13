import logging
from json import JSONDecodeError

import requests
import time

from django.conf import settings

from barriers.models import Assessment, Barrier
from interactions.models import HistoryItem, Interaction

from utils.exceptions import APIException, ScanError
from utils.metadata import (
    OPEN_PENDING_ACTION,
    OPEN_IN_PROGRESS,
    RESOLVED_IN_PART,
    RESOLVED_IN_FULL,
    DORMANT,
    UNKNOWN,
)


logger = logging.getLogger(__name__)


class MarketAccessAPIClient:
    def __init__(self, token=None, **kwargs):
        self.token = token or settings.TRUSTED_USER_TOKEN
        self.barriers = BarriersResource(self)
        self.documents = DocumentsResource(self)
        self.interactions = InteractionsResource(self)
        self.notes = NotesResource(self)

    def request(self, method, path, **kwargs):
        url = f'{settings.MARKET_ACCESS_API_URI}{path}'
        headers = {
            'Authorization': f"Bearer {self.token}",
            'X-User-Agent': '',
            'X-Forwarded-For': '',
        }
        response = getattr(requests, method)(url, headers=headers, **kwargs)
        response.raise_for_status()
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
        try:
            response = self.request(method, path, **kwargs)
            return self.get_results_from_response_data(response.json())
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

    def get_team_members(self, barrier_id, **kwargs):
        url = f"barriers/{barrier_id}/members"
        return self.client.get(url, params=kwargs)

    def add_team_member(self, barrier_id, user_id, role, **kwargs):
        url = f"barriers/{barrier_id}/members"
        data = {
            'user': {
                'profile': {
                    'sso_user_id': user_id,
                }
            },
            'role': role,
        }
        return self.client.post(url, json=data)

    def delete_team_member(self, team_member_id, **kwargs):
        url = f"barriers/members/{team_member_id}"
        return self.client.delete(url, params=kwargs)

    def get_assessment(self, barrier_id):
        url = f"barriers/{barrier_id}/assessment"
        return Assessment(self.client.get(url))

    def create_assessment(self, barrier_id, **kwargs):
        url = f"barriers/{barrier_id}/assessment"
        return self.client.post(url, json=kwargs)

    def update_assessment(self, barrier_id, **kwargs):
        url = f"barriers/{barrier_id}/assessment"
        return self.client.patch(url, json=kwargs)

    def get_csv(self, *args, **kwargs):
        url = f"barriers/export"
        return self.client.get(url, params=kwargs, json=False)

    def set_status(self, barrier_id, status, **kwargs):
        if status == UNKNOWN:
            url = f"barriers/{barrier_id}/unknown"
        if status == OPEN_PENDING_ACTION:
            url = f"barriers/{barrier_id}/open-action_required"
        elif status == OPEN_IN_PROGRESS:
            url = f"barriers/{barrier_id}/open-in-progress"
        elif status == RESOLVED_IN_PART:
            url = f"barriers/{barrier_id}/resolve-in-part"
        elif status == RESOLVED_IN_FULL:
            url = f"barriers/{barrier_id}/resolve-in-full"
        elif status == DORMANT:
            url = f"barriers/{barrier_id}/hibernate"
        return self.client.put(url, json=kwargs)


class InteractionsResource(Resource):
    resource_name = "interactions"
    model = Interaction

    def list(self, barrier_id, **kwargs):
        url = f"barriers/{barrier_id}/interactions"
        return [
            self.model(result)
            for result in self.client.get(url, params=kwargs)['results']
        ]

    def delete_note(self, note_id):
        return self.client.delete(f"barriers/interactions/{note_id}")


class NotesResource(Resource):
    resource_name = "notes"
    model = Interaction

    def create(self, barrier_id, *args, **kwargs):
        url = f"barriers/{barrier_id}/interactions"
        return self.model(self.client.post(url, json=kwargs))

    def update(self, id, *args, **kwargs):
        url = f"barriers/interactions/{id}"
        return self.model(self.client.patch(url, json=kwargs))


class DocumentsResource(Resource):
    def create(self, filename, filesize):
        return self.client.post(
            "documents",
            json={
                "original_filename": filename,
                "size": filesize,
            }
        )

    def complete_upload(self, document_id):
        return self.client.post(f"documents/{document_id}/upload-callback")

    def check_scan_status(self, document_id):
        max_wait_time = settings.FILE_SCAN_MAX_WAIT_TIME
        interval = settings.FILE_SCAN_STATUS_CHECK_INTERVAL

        url = f"documents/{document_id}/upload-callback"
        max_attempts = int(max_wait_time / interval)

        for i in range(max_attempts):
            try:
                response = self.client.post(url)
            except requests.exceptions.HTTPError:
                raise ScanError("Unable to get scan status")

            if response.get('status') == "virus_scanning_failed":
                raise ScanError(
                    "This file may be infected with a virus and will not be "
                    "accepted."
                )
            elif response.get('status') == "virus_scanned":
                return

            time.sleep(interval / 1000)

        raise ScanError("Virus scan took too long")

    def get_download(self, document_id):
        return self.client.get(f"documents/{document_id}/download")
