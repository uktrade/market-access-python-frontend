import json

from django.conf import settings
from django.test import TestCase, override_settings
from mock import patch

from barriers.models.history import HistoryItem
from core.filecache import memfiles
from users.models import User
from utils.api.resources import (
    ActionPlanMilestoneResource,
    ActionPlanResource,
    ActionPlanStakeholderResource,
    ActionPlanTaskResource,
    BarriersResource,
    NotesResource,
    PublicBarriersResource,
    ReportsResource,
    UsersResource,
)


@override_settings(API_RESULTS_LIMIT=10)
class MarketAccessTestCase(TestCase):
    _barriers = None
    _draft_barriers = ()
    _history = None
    _team_members = None
    _users = None
    barrier_index = 0
    draft_barrier_index = 0
    administrator = User(
        {
            "is_superuser": False,
            "is_active": True,
            "permissions": [
                "change_user",
                "list_users",
                "set_topprioritybarrier",
                "can_approve_estimated_completion_date",
            ],
            "groups": [{"id": 4, "name": "Administrator"}],
        }
    )
    general_user = User(
        {
            "is_superuser": False,
            "is_active": True,
            "permissions": [],
            "groups": [],
        }
    )
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
            "groups": [{"id": 27, "name": "Public barrier approver"}],
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
            "groups": [{"id": 5, "name": "Analyst"}],
        }
    )
    publisher_user = User(
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
            "groups": [{"id": 6, "name": "Publisher"}],
        }
    )

    public_barrier_activity = [
        HistoryItem(
            {
                "date": "2020-03-19T09:18:16.687291Z",
                "model": "public_barrier",
                "field": "public_view_status",
                "old_value": {
                    "public_view_status": {"id": 0, "name": "Unknown"},
                    "public_eligibility": False,
                    "public_eligibility_summary": "",
                },
                "new_value": {
                    "public_view_status": {"id": 10, "name": "Allowed"},
                    "public_eligibility": True,
                    "public_eligibility_summary": "",
                },
                "user": {"id": 48, "name": "Test-user"},
            }
        ),
        HistoryItem(
            {
                "date": "2020-03-19T09:18:16.687291Z",
                "model": "public_barrier",
                "field": "public_view_status",
                "old_value": {
                    "public_view_status": {"id": 70, "name": "Awaiting approval"},
                    "public_eligibility": True,
                    "public_eligibility_summary": "",
                },
                "new_value": {
                    "public_view_status": {"id": 30, "name": "Awaiting publishing"},
                    "public_eligibility": True,
                    "public_eligibility_summary": "",
                },
                "user": {"id": 48, "name": "Test-user"},
            }
        ),
        HistoryItem(
            {
                "date": "2020-03-19T09:18:16.687291Z",
                "model": "public_barrier",
                "field": "public_view_status",
                "old_value": {
                    "public_view_status": {"id": 30, "name": "Awaiting publishing"},
                    "public_eligibility": True,
                    "public_eligibility_summary": "",
                },
                "new_value": {
                    "public_view_status": {"id": 40, "name": "Published"},
                    "public_eligibility": True,
                    "public_eligibility_summary": "",
                },
                "user": {"id": 48, "name": "Test-user"},
            }
        ),
    ]

    def setUp(self):
        self.init_session()
        self.init_get_barrier_patcher()
        self.init_get_draft_barrier_patcher()
        self.init_get_activity_patcher()
        self.init_get_interactions_patcher()
        self.init_get_current_user_patcher()
        self.init_get_public_barrier_patcher()
        self.init_get_action_plans_patcher()

    def init_session(self):
        session = self.client.session
        session.update(
            {
                "sso_token": "abcd",
                "user_data": {
                    "id": 49,
                    "username": "test user",
                },
            }
        )
        session.save()

    def init_get_barrier_patcher(self):
        self.get_barrier_patcher = patch("utils.api.resources.BarriersResource.get")
        self.mock_get_barrier = self.get_barrier_patcher.start()
        self.mock_get_barrier.return_value = BarriersResource.model(
            self.barriers[self.barrier_index]
        )
        self.addCleanup(self.get_barrier_patcher.stop)

    def init_get_draft_barrier_patcher(self):
        self.get_draft_barrier_patcher = patch(
            "utils.api.resources.ReportsResource.get"
        )
        self.mock_get_draft_barrier = self.get_draft_barrier_patcher.start()
        self.mock_get_draft_barrier.return_value = ReportsResource.model(
            self.draft_barriers[self.draft_barrier_index]
        )
        self.addCleanup(self.get_draft_barrier_patcher.stop)

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
        self.get_barrier_action_plan_patcher = patch(
            "utils.api.resources.ActionPlanResource.get_barrier_action_plan"
        )
        self.get_barrier_action_plan = self.get_barrier_action_plan_patcher.start()
        self.get_barrier_action_plan.return_value = self.action_plans
        self.addCleanup(self.get_barrier_action_plan_patcher.stop)

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
    def draft_barriers(self):
        if not self._draft_barriers:
            file = f"{settings.BASE_DIR}/../tests/reports/fixtures/draft_barriers.json"
            self._draft_barriers = json.loads(memfiles.open(file))
        return self._draft_barriers

    @property
    def draft_barrier(self):
        return self.draft_barriers[self.barrier_index]

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
                "stakeholders": [
                    self.action_plan_individual_stakeholder.data,
                    self.action_plan_organisation_stakeholder.data,
                ],
                "milestones": [self.action_plan_milestone.data],
                "current_status": "adsaasdasdasd",
                "current_status_last_updated": "2021-07-08T09:03:36.246039Z",
                "owner_email": "james.pacileo@digital.trade.gov.uk",
                "status": "ON_TRACK",
                "strategic_context": "asdasdasd",
            }
        )

    @property
    def action_plan_milestone(self):
        return ActionPlanMilestoneResource.model(
            {
                "id": "f142480b-71f5-439c-9ad8-b43e4be382c2",
                "action_plan": "83d08628-9442-4bad-8038-7a5e2a07d9b1",
                "objective": "Do all kinds of amazing things.",
                "completion_date": None,
                "tasks": [
                    self.action_plan_task.data,
                ],
            }
        )

    @property
    def action_plan_task(self):
        return ActionPlanTaskResource.model(
            {
                "id": "d42f69b3-707a-4df2-b259-e8a4040e1791",
                "milestone": "f142480b-71f5-439c-9ad8-b43e4be382c2",
                "action_text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
                "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
                "status": "NOT_STARTED",
                "start_date": "2022-07-01",
                "completion_date": "2022-12-01",
                "action_type": "MULTILATERAL_ENGAGEMENT",
                "action_type_category": "With OECD",
                "assigned_stakeholders": [
                    self.action_plan_individual_stakeholder.data,
                    self.action_plan_organisation_stakeholder.data,
                ],
                "action_type_display": "Multilateral engagement - With OECD",
                "assigned_to": 16,
                "assigned_to_email": "Tre.Ratke46@hotmail.testfake",
                "outcome": "",
                "progress": "",
            }
        )

    @property
    def action_plan_individual_stakeholder(self):
        return ActionPlanStakeholderResource.model(
            {
                "id": "b44e4818-0c96-4133-99e5-defacf4892bd",
                "action_plan": "83d08628-9442-4bad-8038-7a5e2a07d9b1",
                "name": "Fred Bloggs",
                "status": "NEUTRAL",
                "organisation": "Doing Nothing Ltd.",
                "job_title": "Doing Something Specialist",
                "is_organisation": False,
            }
        )

    @property
    def action_plan_organisation_stakeholder(self):
        return ActionPlanStakeholderResource.model(
            {
                "id": "af99d5fd-754a-48ae-9dbe-bba68cdf6853",
                "action_plan": "83d08628-9442-4bad-8038-7a5e2a07d9b1",
                "name": "Useless Gmbh.",
                "status": "BLOCKER",
                "organisation": "",
                "job_title": "",
                "is_organisation": True,
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
