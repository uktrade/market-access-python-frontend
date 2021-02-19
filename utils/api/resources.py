import time

import requests
from django.conf import settings
from django.core.cache import cache

from barriers.constants import Statuses
from barriers.models import (Barrier, Commodity, EconomicAssessment,
                             EconomicImpactAssessment, HistoryItem, Note,
                             PublicBarrier, PublicBarrierNote,
                             ResolvabilityAssessment, SavedSearch,
                             StrategicAssessment)
from reports.models import Report
from users.models import Group, User
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
            data=response_data["results"],
            total_count=response_data["count"],
        )

    def get(self, id, *args, **kwargs):
        url = f"{self.resource_name}/{id}"
        return self.model(self.client.get(url, *args, **kwargs))

    def patch(self, id, *args, **kwargs):
        url = f"{self.resource_name}/{id}"
        return self.model(self.client.patch(url, json=kwargs))

    def create(self, *args, **kwargs):
        return self.model(self.client.post(self.resource_name, json=kwargs))

    def update(self, id, *args, **kwargs):
        url = f"{self.resource_name}/{id}"
        return self.model(self.client.put(url, data=kwargs))

    def delete(self, id, *args, **kwargs):
        url = f"{self.resource_name}/{id}"
        return self.client.delete(url)


class BarriersResource(APIResource):
    resource_name = "barriers"
    model = Barrier

    def get_activity(self, barrier_id, **kwargs):
        url = f"barriers/{barrier_id}/activity"
        return [
            HistoryItem(result)
            for result in self.client.get(url, params=kwargs)["history"]
        ]

    def get_history(self, barrier_id, **kwargs):
        url = f"barriers/{barrier_id}/history"
        return [
            HistoryItem(result)
            for result in self.client.get(url, params=kwargs)["history"]
        ]

    def get_full_history(self, barrier_id, **kwargs):
        url = f"barriers/{barrier_id}/full_history"
        return [
            HistoryItem(result)
            for result in self.client.get(url, params=kwargs)["history"]
        ]

    def get_team_members(self, barrier_id, **kwargs):
        url = f"barriers/{barrier_id}/members"
        response_data = self.client.get(url, params=kwargs)
        return response_data.get("results", [])

    def get_team_member(self, member_id):
        url = f"barriers/members/{member_id}"
        response_data = self.client.get(url)
        return response_data

    def patch_team_member(self, member_id, payload):
        url = f"barriers/members/{member_id}"
        response_data = self.client.patch(url, json=payload)
        return response_data

    def add_team_member(self, barrier_id, user_id, role, **kwargs):
        url = f"barriers/{barrier_id}/members"
        data = {
            "user": {"profile": {"sso_user_id": user_id,}},
            "role": role,
        }
        return self.client.post(url, json=data)

    def delete_team_member(self, team_member_id, **kwargs):
        url = f"barriers/members/{team_member_id}"
        return self.client.delete(url, params=kwargs)

    def get_csv(self, *args, **kwargs):
        url = "barriers/s3-download"
        return self.client.get(url, params=kwargs).get("url")

    def get_streamed_csv(self, *args, **kwargs):
        url = "barriers/export"
        return self.client.get(url, params=kwargs, stream=True, raw=True)

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


class NotesResource(APIResource):
    resource_name = "interactions"
    model = Note

    def create(self, barrier_id, *args, **kwargs):
        url = f"barriers/{barrier_id}/interactions"
        return self.model(self.client.post(url, json=kwargs))

    def delete(self, note_id):
        return self.client.delete(f"barriers/interactions/{note_id}")

    def list(self, barrier_id, **kwargs):
        url = f"barriers/{barrier_id}/interactions"
        return [
            self.model(result)
            for result in self.client.get(url, params=kwargs)["results"]
        ]

    def update(self, id, *args, **kwargs):
        url = f"barriers/interactions/{id}"
        return self.model(self.client.patch(url, json=kwargs))


class DocumentsResource(APIResource):
    def create(self, filename, filesize):
        return self.client.post(
            "documents", json={"original_filename": filename, "size": filesize,}
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

            if response.get("status") == "virus_scanning_failed":
                raise ScanError("Unable to virus scan the file")
            elif response.get("status") == "virus_scanned":
                if "av_clean" not in response or response.get("av_clean") is True:
                    return
                raise ScanError(
                    "This file may be infected with a virus and will not be accepted."
                )

            time.sleep(interval / 1000)

        raise ScanError("Virus scan took too long")

    def get_download(self, document_id):
        return self.client.get(f"documents/{document_id}/download")


class UsersResource(APIResource):
    resource_name = "users"
    model = User

    def get_current(self):
        user_data = self.client.get("whoami")
        self.update_cached_user_data(user_data)
        return self.model(user_data)

    def patch(self, *args, **kwargs):
        user = super().patch(*args, **kwargs)
        self.update_cached_user_data(user.data)
        return user

    def update_cached_user_data(self, user_data):
        user_id = user_data.get("id")
        cache_key = f"user_data:{user_id}"
        cached_data = cache.get(cache_key, user_data)
        cached_data.update(user_data)
        cache.set(cache_key, cached_data, settings.USER_DATA_CACHE_TIME)


class ReportsResource(APIResource):
    resource_name = "reports"
    model = Report

    def submit(self, barrier_id):
        return self.client.put(f"reports/{barrier_id}/submit")


class SavedSearchesResource(APIResource):
    resource_name = "saved-searches"
    model = SavedSearch


class GroupsResource(APIResource):
    resource_name = "groups"
    model = Group


class CommoditiesResource(APIResource):
    resource_name = "commodities"
    model = Commodity


class PublicBarrierNotesResource(APIResource):
    resource_name = "public-barrier-notes"
    model = PublicBarrierNote


class PublicBarriersResource(APIResource):
    resource_name = "public-barriers"
    model = PublicBarrier

    def get_activity(self, barrier_id, **kwargs):
        url = f"public-barriers/{barrier_id}/activity"
        return [
            HistoryItem(result)
            for result in self.client.get(url, params=kwargs)["history"]
        ]

    def create_note(self, id, *args, **kwargs):
        return self.client.post(f"{self.resource_name}/{id}/notes", json=kwargs)

    def get_notes(self, id, *args, **kwargs):
        return [
            PublicBarrierNote(note)
            for note in self.client.get(f"{self.resource_name}/{id}/notes")["results"]
        ]

    def ignore_all_changes(self, id):
        return self.client.post(f"{self.resource_name}/{id}/ignore-all-changes")

    def mark_as_in_progress(self, id):
        return self.client.post(f"{self.resource_name}/{id}/unprepared")

    def mark_as_ready(self, id):
        return self.client.post(f"{self.resource_name}/{id}/ready")

    def publish(self, id):
        return self.client.post(f"{self.resource_name}/{id}/publish")

    def unpublish(self, id):
        return self.client.post(f"{self.resource_name}/{id}/unpublish")


class EconomicAssessmentResource(APIResource):
    resource_name = "economic-assessments"
    model = EconomicAssessment


class EconomicImpactAssessmentResource(APIResource):
    resource_name = "economic-impact-assessments"
    model = EconomicImpactAssessment


class ResolvabilityAssessmentResource(APIResource):
    resource_name = "resolvability-assessments"
    model = ResolvabilityAssessment


class StrategicAssessmentResource(APIResource):
    resource_name = "strategic-assessments"
    model = StrategicAssessment
