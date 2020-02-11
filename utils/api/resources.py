import requests
import time

from django.conf import settings

from barriers.constants import Statuses
from barriers.models import Assessment, Barrier, HistoryItem, Interaction
from reports.models import Report
from users.models import User

from utils.exceptions import ScanError
from utils.models import ModelList


class APIResource:
    resource_name = None
    model = None

    def __init__(self, client):
        self.client = client

    def list(self, **kwargs):
        response_data = self.client.get(self.resource_name, params=kwargs)
        return ModelList(
            model=self.model,
            data=response_data['results'],
            total_count=response_data['count'],
        )

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

    def delete(self, id, *args, **kwargs):
        url = f"{self.resource_name}/{id}"
        return self.client.delete(url)


class BarriersResource(APIResource):
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
        response_data = self.client.get(url, params=kwargs)
        return response_data.get('results', [])

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
        return self.client.get(url, params=kwargs, raw=True)

    def set_status(self, barrier_id, status, **kwargs):
        if status == Statuses.UNKNOWN:
            url = f"barriers/{barrier_id}/unknown"
        elif status == Statuses.OPEN_PENDING_ACTION:
            url = f"barriers/{barrier_id}/open-action_required"
        elif status == Statuses.OPEN_IN_PROGRESS:
            url = f"barriers/{barrier_id}/open-in-progress"
        elif status == Statuses.RESOLVED_IN_PART:
            url = f"barriers/{barrier_id}/resolve-in-part"
        elif status == Statuses.RESOLVED_IN_FULL:
            url = f"barriers/{barrier_id}/resolve-in-full"
        elif status == Statuses.DORMANT:
            url = f"barriers/{barrier_id}/hibernate"
        return self.client.put(url, json=kwargs)


class InteractionsResource(APIResource):
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


class NotesResource(APIResource):
    resource_name = "notes"
    model = Interaction

    def create(self, barrier_id, *args, **kwargs):
        url = f"barriers/{barrier_id}/interactions"
        return self.model(self.client.post(url, json=kwargs))

    def update(self, id, *args, **kwargs):
        url = f"barriers/interactions/{id}"
        return self.model(self.client.patch(url, json=kwargs))


class DocumentsResource(APIResource):
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


class UsersResource(APIResource):
    resource_name = "users"
    model = User

    def patch(self, *args, **kwargs):
        return self.client.patch("whoami", json=kwargs)


class ReportsResource(APIResource):
    resource_name = "reports"
    model = Report
