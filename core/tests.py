import json

from django.conf import settings
from django.test import TestCase, override_settings
from mock import patch
from users.models import User
from utils.api.resources import (ActionPlanResource, BarriersResource,
                                 NotesResource, PublicBarriersResource,
                                 UsersResource)

from core.filecache import memfiles


@override_settings(API_RESULTS_LIMIT=10)
class MarketAccessTestCase(TestCase):
    _barriers = None
    _history = None
    _team_members = None
    _users = None
    barrier_index = 0
    administrator = User(
        {
            "is_superuser": False,
            "is_active": True,
            "permissions": ["change_user", "list_users"],
        }
    )
    general_user = User({"is_superuser": False, "is_active": True, "permissions": [],})
    approver_user = User(
        {
            "is_superuser": False,
            "is_active": True,
            "permissions": [
                "add_resolvabilityassessment",
                "change_resolvabilityassessment",
                "archive_resolvabilityassessment",
                "approve_resolvabilityassessment",
                "add_strategicassessment",
                "change_strategicassessment",
                "archive_strategicassessment",
                "approve_strategicassessment",
            ],
        }
    )
    analyst_user = User(
        {
            "is_superuser": False,
            "is_active": True,
            "permissions": [
                "add_economicassessment",
                "change_economicassessment",
                "archive_economicassessment",
                "approve_economicassessment",
                "add_economicimpactassessment",
                "change_economicimpactassessment",
                "archive_economicimpactassessment",
            ],
        }
    )

    def setUp(self):
        self.init_session()
        self.init_get_barrier_patcher()
        self.init_get_activity_patcher()
        self.init_get_interactions_patcher()
        self.init_get_current_user_patcher()
        self.init_get_public_barrier_patcher()
        self.init_get_action_plans_patcher()

    def init_session(self):
        session = self.client.session
        session.update(
            {"sso_token": "abcd", "user_data": {"id": 49, "username": "test user",},}
        )
        session.save()

    def init_get_barrier_patcher(self):
        self.get_barrier_patcher = patch("utils.api.resources.BarriersResource.get")
        self.mock_get_barrier = self.get_barrier_patcher.start()
        self.mock_get_barrier.return_value = BarriersResource.model(
            self.barriers[self.barrier_index]
        )
        self.addCleanup(self.get_barrier_patcher.stop)

    def init_get_activity_patcher(self):
        self.get_activity_patcher = patch(
            "utils.api.resources.BarriersResource.get_activity"
        )
        self.mock_get_activity = self.get_activity_patcher.start()
        self.mock_get_activity.return_value = []
        self.addCleanup(self.get_activity_patcher.stop)

    def init_get_interactions_patcher(self):
        self.get_interactions_patcher = patch("utils.api.resources.NotesResource.list")
        self.mock_get_interactions = self.get_interactions_patcher.start()
        self.mock_get_interactions.return_value = self.notes
        self.addCleanup(self.get_interactions_patcher.stop)

    def init_get_current_user_patcher(self):
        self.get_current_user_patcher = patch(
            "utils.api.resources.UsersResource.get_current"
        )
        self.get_current_user = self.get_current_user_patcher.start()
        self.get_current_user.return_value = self.current_user
        self.addCleanup(self.get_current_user_patcher.stop)

    def init_get_action_plans_patcher(self):
        self.get_barrier_action_plan = patch(
            "utils.api.resources.ActionPlanResource.get_barrier_action_plan"
        )
        self.get_barrier_action_plan = self.get_barrier_action_plan.start()
        self.get_barrier_action_plan.return_value = self.action_plans
        self.addCleanup(self.get_barrier_action_plan.stop)

    def init_get_public_barrier_patcher(self):
        self.get_public_barrier_patcher = patch(
            "utils.api.resources.PublicBarriersResource.get"
        )
        self.mock_get_public_barrier = self.get_public_barrier_patcher.start()
        self.mock_get_public_barrier.return_value = PublicBarriersResource.model(
            self.public_barrier
        )
        self.addCleanup(self.get_public_barrier_patcher.stop)

    def delete_session_key(self, key):
        try:
            del self.client.session[key]
        except KeyError:
            pass

    def update_session(self, data):
        session = self.client.session
        session.update(data)
        session.save()

    @property
    def barriers(self):
        if self._barriers is None:
            file = f"{settings.BASE_DIR}/../tests/barriers/fixtures/barriers.json"
            self._barriers = json.loads(memfiles.open(file))
        return self._barriers

    @property
    def all_history(self):
        if self._history is None:
            file = f"{settings.BASE_DIR}/../tests/barriers/fixtures/history.json"
            self._history = json.loads(memfiles.open(file))
        return self._history

    @property
    def barrier(self):
        return self.barriers[self.barrier_index]

    @property
    def public_barrier(self):
        return {
            "title": "Public Title",
            "summary": "Public summary",
            "public_view_status": 20,
            "status": 0,
            "is_resolved": False,
            "internal_is_resolved": False,
            "status_date": None,
            "internal_status_date": None,
        }

    @property
    def history(self):
        # goes hand in hand with self.barriers
        return self.all_history[0]

    @property
    def current_user(self):
        return UsersResource.model(
            {
                "id": 49,
                "username": "test user",
                "profile": {"sso_user_id": "c12195ed-bf30-4a67-ba73-e95cfe012f77"},
                "email": "test@test.com",
                "first_name": "Geraldine",
                "last_name": "Kshlerin",
                "full_name": "Geraldine Kshlerin",
                "is_superuser": True,
                "is_active": True,
                "permissions": [],
            }
        )

    @property
    def action_plans(self):
        return ActionPlanResource.model(
            {
                "id": "83d08628-9442-4bad-8038-7a5e2a07d9b1",
                "barrier": "ad217252-7b11-4c7b-885b-6d017a4c0812",
                "owner": 49,
                "milestones": [
                    {
                        "id": "0d0a29c8-48f3-4e0c-bac7-72f1f3960673",
                        "action_plan": "83d08628-9442-4bad-8038-7a5e2a07d9b1",
                        "objective": "ghfgh",
                        "completion_date": "2021-10-01",
                        "tasks": [
                            {
                                "id": "5dbea476-7aa3-4579-b6f3-b4036f4c1b76",
                                "milestone": "0d0a29c8-48f3-4e0c-bac7-72f1f3960673",
                                "status": "IN_PROGRESS",
                                "start_date": "2021-10-01",
                                "completion_date": "2022-10-01",
                                "action_text": "asdasdas",
                                "action_type": "PLURILATERAL_ENGAGEMENT",
                                "action_type_category": "With the EU",
                                "stakeholders": "asdasd",
                                "action_type_display": "Plurilateral engagement - With the EU",
                                "assigned_to": 76,
                                "assigned_to_email": "aaron.jaswal@trade.gov.uk",
                                "outcome": "",
                                "progress": "",
                            }
                        ],
                    },
                    {
                        "id": "c515c3bc-3541-414c-b92f-0e8ec2be37a2",
                        "action_plan": "83d08628-9442-4bad-8038-7a5e2a07d9b1",
                        "objective": "bvvcbcvb",
                        "completion_date": None,
                        "tasks": [],
                    },
                ],
                "current_status": "adsaasdasdasd",
                "current_status_last_updated": "2021-07-08T09:03:36.246039Z",
                "owner_email": "james.pacileo@digital.trade.gov.uk",
                "status": "ON_TRACK",
                "strategic_context": "asdasdasd",
                "strategic_context_last_updated": "2021-07-08T09:03:36.246039Z",
            }
        )

    @property
    def notes(self):
        return [
            NotesResource.model(
                {
                    "id": 1,
                    "kind": "Comment",
                    "text": "Comment with document",
                    "pinned": False,
                    "is_active": True,
                    "documents": [
                        {
                            "id": "cd5ada56-53ee-4324-a2fa-b2f90f47ccbd",
                            "name": "test.jpeg",
                            "size": 5159,
                            "status": "virus_scanned",
                        },
                    ],
                    "created_on": "2020-01-20T12:00:00.683297Z",
                    "created_by": {"id": 1, "name": "Test-user"},
                }
            ),
            NotesResource.model(
                {
                    "id": 2,
                    "kind": "Comment",
                    "text": "Comment without document",
                    "pinned": False,
                    "is_active": True,
                    "documents": [],
                    "created_on": "2020-01-21T09:30:00.714208Z",
                    "created_by": {"id": 1, "name": "Test-user"},
                }
            ),
        ]

    @property
    def team_members(self):
        if self._team_members is None:
            file = f"{settings.BASE_DIR}/../tests/barriers/fixtures/team_members.json"
            self._team_members = json.loads(memfiles.open(file))
        return self._team_members

    @property
    def users(self):
        if self._users is None:
            file = f"{settings.BASE_DIR}/../tests/barriers/fixtures/users.json"
            users = json.loads(memfiles.open(file))
            self._users = [User(user) for user in users]
        return self._users


class ReportsTestsMixin:
    _draft_barriers = ()

    @property
    def draft_barriers(self):
        if not self._draft_barriers:
            file = f"{settings.BASE_DIR}/../tests/reports/fixtures/draft_barriers.json"
            self._draft_barriers = json.loads(memfiles.open(file))
        return self._draft_barriers

    def draft_barrier(self, step):
        """
        Returns the fixture that corresponds with the step number.
        """
        for data in self.draft_barriers:
            if int(data.get("step")) == int(step):
                return data


class ReportsTestCase(ReportsTestsMixin, MarketAccessTestCase):
    pass
