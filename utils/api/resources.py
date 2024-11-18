from __future__ import annotations

import logging
import time
import urllib.parse
from typing import TYPE_CHECKING

import requests
from django.conf import settings
from django.core.cache import cache

from barriers.constants import Statuses
from barriers.models import (
    ActionPlan,
    Barrier,
    BarrierDownload,
    Commodity,
    EconomicAssessment,
    EconomicImpactAssessment,
    HistoryItem,
    Note,
    PublicBarrier,
    PublicBarrierNote,
    ResolvabilityAssessment,
    SavedSearch,
    Stakeholder,
    StrategicAssessment,
)
from barriers.models.action_plans import ActionPlanTask, Milestone
from barriers.models.feedback import Feedback
from barriers.models.history.mentions import Mention, NotificationExclusion
from reports.models import Report
from users.models import DashboardTask, Group, User, UserProfile
from utils.exceptions import ScanError
from utils.models import APIModel, ModelList

if TYPE_CHECKING:
    from utils.api.client import MarketAccessAPIClient

logger = logging.getLogger(__name__)


class APIResource:
    resource_name = None
    model = None
    client: MarketAccessAPIClient

    def __init__(self, client) -> None:
        self.client = client

    def list(self, **kwargs) -> ModelList:
        response_data = self.client.get(self.resource_name, params=kwargs)
        return ModelList(
            model=self.model,
            data=response_data["results"],
            total_count=response_data["count"],
        )

    def get(self, id=None, *args, **kwargs) -> APIModel:
        if not id:
            url = f"{self.resource_name}"
        else:
            url = f"{self.resource_name}/{id}"
        return self.model(self.client.get(url, *args, **kwargs))

    def patch(self, id, *args, **kwargs) -> APIModel:
        url = f"{self.resource_name}/{id}"
        return self.model(self.client.patch(url, json=kwargs))

    def create(self, *args, **kwargs) -> APIModel:
        return self.model(self.client.post(self.resource_name, json=kwargs))

    def update(self, id, *args, **kwargs) -> APIModel:
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
            "user": {
                "profile": {
                    "sso_user_id": user_id,
                }
            },
            "role": role,
        }
        return self.client.post(url, json=data)

    def delete_team_member(self, team_member_id, **kwargs):
        url = f"barriers/members/{team_member_id}"
        return self.client.delete(url, params=kwargs)

    def request_download_approval(self):
        url = "barriers/request-download-approval"
        return self.client.post(url)

    def request_download_permissions(self, *args, **kwargs):
        url = "barriers/request-download-permissions"
        return self.client.get(url, params=kwargs)

    def set_status(self, barrier_id, status, **kwargs):
        if status == Statuses.UNKNOWN:
            url = f"barriers/{barrier_id}/unknown"
        elif status == Statuses.OPEN_IN_PROGRESS:
            url = f"barriers/{barrier_id}/open-in-progress"
        elif status == Statuses.RESOLVED_IN_PART:
            url = f"barriers/{barrier_id}/resolve-in-part"
        elif status == Statuses.RESOLVED_IN_FULL:
            url = f"barriers/{barrier_id}/resolve-in-full"
        elif status == Statuses.DORMANT:
            url = f"barriers/{barrier_id}/hibernate"
        return self.client.put(url, json=kwargs)

    def create_top_100_progress_update(self, **kwargs):
        return self.client.post(
            f"barriers/{kwargs['barrier']}/top_100_progress_updates", data=kwargs
        )

    def patch_top_100_progress_update(self, **kwargs):
        return self.client.patch(
            f"barriers/{kwargs['barrier']}/top_100_progress_updates/{kwargs['id']}",
            data=kwargs,
        )

    def get_top_priority_summary(self, **kwargs):
        return self.client.get(
            f"barriers/{kwargs['barrier']}/top_priority_summary/{kwargs['barrier']}",
            data=kwargs,
        )

    def create_top_priority_summary(self, **kwargs):
        return self.client.post(
            f"barriers/{kwargs['barrier']}/top_priority_summary", data=kwargs
        )

    def patch_top_priority_summary(self, **kwargs):
        return self.client.patch(
            f"barriers/{kwargs['barrier']}/top_priority_summary/{kwargs['barrier']}",
            data=kwargs,
        )

    def create_programme_fund_progress_update(self, **kwargs):
        return self.client.post(
            f"barriers/{kwargs['barrier']}/programme_fund_progress_updates", data=kwargs
        )

    def patch_programme_fund_progress_update(self, **kwargs):
        return self.client.patch(
            f"barriers/{kwargs['barrier']}/programme_fund_progress_updates/{kwargs['id']}",
            data=kwargs,
        )

    def create_next_steps_item(self, **kwargs):
        return self.client.post(
            f"barriers/{kwargs['barrier']}/next_steps_items", data=kwargs
        )

    def patch_next_steps_item(self, **kwargs):
        return self.client.patch(
            f"barriers/{kwargs['barrier']}/next_steps_items/{kwargs['id']}",
            data=kwargs,
        )

    def get_similar(self, barrier_id, **kwargs):
        # using the word similar her not to confuse with
        # django related objects
        url = f"barriers/{barrier_id}/related-barriers"
        similar_barriers = self.client.get(url, params=kwargs)
        return similar_barriers


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
            "documents",
            json={
                "original_filename": filename,
                "size": filesize,
            },
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


class DashboardTasksResource(APIResource):
    resource_name = "dashboard-tasks"
    model = DashboardTask


class CommoditiesResource(APIResource):
    resource_name = "commodities"
    model = Commodity


class PublicBarrierNotesResource(APIResource):
    resource_name = "public-barrier-notes"
    model = PublicBarrierNote


class PublicBarriersResource(APIResource):
    resource_name = "public-barriers"
    model = PublicBarrier

    def allow_for_publishing_process(self, id):
        return self.client.post(
            f"{self.resource_name}/{id}/allow-for-publishing-process"
        )

    def report_public_barrier_title(self, id, *args, **kwargs):
        return self.client.post(
            f"{self.resource_name}/{id}/report_public_barrier_title", json=kwargs
        )

    def report_public_barrier_summary(self, id, *args, **kwargs):
        return self.client.post(
            f"{self.resource_name}/{id}/report_public_barrier_summary", json=kwargs
        )

    def ready_for_approval(self, id):
        return self.client.post(f"{self.resource_name}/{id}/ready-for-approval")

    def ready_for_publishing(self, id):
        return self.client.post(f"{self.resource_name}/{id}/ready-for-publishing")

    def publish(self, id):
        return self.client.post(f"{self.resource_name}/{id}/publish")

    def unpublish(self, id):
        return self.client.post(f"{self.resource_name}/{id}/unpublish")

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


class MentionResource(APIResource):
    resource_name = "mentions"
    model = Mention

    def mark_as_read(self, mention_id, *args, **kwargs):
        url = f"mentions/mark-as-read/{mention_id}"
        return self.model(self.client.get(url))

    def mark_as_unread(self, mention_id):
        url = f"mentions/mark-as-unread/{mention_id}"
        return self.model(self.client.get(url))

    def mark_all_as_read(self):
        url = "mentions/mark-all-as-read"
        return self.model(self.client.get(url))

    def mark_all_as_unread(self):
        url = "mentions/mark-all-as-unread"
        return self.model(self.client.get(url))


class NotificationExclusionResource(APIResource):
    resource_name = "mentions/exclude-from-notifications"
    model = NotificationExclusion

    def turn_off_notifications(self):
        url = "mentions/exclude-from-notifications"
        return self.model(self.client.post(url))

    def turn_on_notifications(self):
        url = "mentions/exclude-from-notifications"
        return self.model(self.client.delete(url))


class ActionPlanResource(APIResource):
    resource_name = "action_plans"
    model = ActionPlan

    def get_barrier_action_plan(self, barrier_id: str):
        url = f"barriers/{barrier_id}/action_plan"
        return self.model(self.client.get(url))

    def edit_action_plan(self, barrier_id, *args, **kwargs):
        url = f"barriers/{barrier_id}/action_plan"
        return self.model(self.client.patch(url, json={**kwargs}))


class ActionPlanMilestoneResource(APIResource):
    resource_name = "action_plan_milestones"
    model = Milestone

    def create_milestone(self, barrier_id, *args, **kwargs):
        url = f"barriers/{barrier_id}/action_plan/milestones"
        return self.model(
            self.client.post(url, json={"barrier": str(barrier_id), **kwargs})
        )

    def update_milestone(self, barrier_id, milestone_id, *args, **kwargs):
        url = f"barriers/{barrier_id}/action_plan/milestones/{milestone_id}"
        return self.model(self.client.patch(url, json={**kwargs}))

    def delete_milestone(self, barrier_id, milestone_id, *args, **kwargs):
        url = f"barriers/{barrier_id}/action_plan/milestones/{milestone_id}"
        return self.client.delete(url)


class ActionPlanTaskResource(APIResource):
    resource_name = "action_plan_tasks"
    model = ActionPlanTask

    def create_task(self, barrier_id, milestone_id, *args, **kwargs):
        url = f"barriers/{barrier_id}/action_plan/tasks"
        return self.model(
            self.client.post(
                url,
                json={
                    "barrier": str(barrier_id),
                    "milestone": str(milestone_id),
                    **kwargs,
                },
            )
        )

    def update_task(self, barrier_id, task_id, *args, **kwargs):
        url = f"barriers/{barrier_id}/action_plan/tasks/{task_id}"
        kwargs["milestone_id"] = str(kwargs["milestone_id"])
        return self.model(self.client.patch(url, json={**kwargs}))

    def delete_task(self, barrier_id, task_id, *args, **kwargs):
        url = f"barriers/{barrier_id}/action_plan/tasks/{task_id}"
        return self.client.delete(url)


class ActionPlanStakeholderResource(APIResource):
    resource_name = "stakeholders"
    model = Stakeholder

    def create_stakeholder(self, *args, **kwargs):
        barrier_id = kwargs.pop("barrier_id")
        url = f"barriers/{barrier_id}/action_plan/stakeholders/"
        response = self.client.post(url, json={**kwargs})
        return self.model(response)

    def update_stakeholder(self, *args, **kwargs):
        id = kwargs.pop("id")
        barrier_id = kwargs.pop("barrier_id")
        url = f"barriers/{barrier_id}/action_plan/stakeholders/{id}/"
        response = self.client.patch(url, json={**kwargs})
        return self.model(response)

    def delete_stakeholder(self, *args, **kwargs):
        id = kwargs.pop("id")
        barrier_id = kwargs.pop("barrier_id")
        url = f"barriers/{barrier_id}/action_plan/stakeholders/{id}/"
        self.client.delete(url, json={**kwargs})


class FeedbackResource(APIResource):
    resource_name = "feedback"
    model = Feedback

    def send_feedback(self, *args, **kwargs):
        return self.client.post("feedback/", json={**kwargs})

    def add_comments(self, feedback_id, *args, **kwargs):
        url = f"feedback/{feedback_id}/"
        return self.client.put(url, json={**kwargs})


class BarrierDownloadsResource(APIResource):
    resource_name = "barrier-downloads"
    model = BarrierDownload

    def get_presigned_url(self, download_id):
        url = f"{self.resource_name}/{download_id}/presigned-url"
        return self.client.get(url)

    def create(self, *args, **kwargs):
        query_string = urllib.parse.urlencode(kwargs)
        url = f"{self.resource_name}?{query_string}"
        return self.model(self.client.post(url, json=kwargs))


class UserProfileResource(APIResource):
    resource_name = "users/profile"
    model = UserProfile
