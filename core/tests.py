import json

from django.test import TestCase

from barriers.models import Assessment
from utils.api.resources import BarriersResource, InteractionsResource

from mock import patch


class MarketAccessTestCase(TestCase):
    _assessments = None
    _barriers = None
    _metadata_json = None

    def setUp(self):
        self.init_session()
        self.init_metadata_patcher()
        self.init_get_barrier_patcher()
        self.init_get_history_patcher()
        self.init_get_interactions_patcher()

    def init_session(self):
        session = self.client.session
        session.update({
            "sso_token": 'abcd',
            "user_data": {'username': 'test user'},
        })
        session.save()

    def init_metadata_patcher(self):
        self.metadata_patcher = patch("utils.metadata.redis_client.get")
        self.mock_metadata_get = self.metadata_patcher.start()
        self.mock_metadata_get.return_value = self.metadata_json
        self.addCleanup(self.metadata_patcher.stop)

    def init_get_barrier_patcher(self):
        self.get_barrier_patcher = patch("utils.api.resources.BarriersResource.get")
        self.mock_get_barrier = self.get_barrier_patcher.start()
        self.mock_get_barrier.return_value = BarriersResource.model(self.barriers[0])
        self.addCleanup(self.get_barrier_patcher.stop)

    def init_get_barrier_patcher(self):
        self.get_barrier_patcher = patch("utils.api.resources.BarriersResource.get")
        self.mock_get_barrier = self.get_barrier_patcher.start()
        self.mock_get_barrier.return_value = BarriersResource.model(self.barriers[0])
        self.addCleanup(self.get_barrier_patcher.stop)

    def init_get_history_patcher(self):
        self.get_history_patcher = patch("utils.api.resources.BarriersResource.get_history")
        self.mock_get_history = self.get_history_patcher.start()
        self.mock_get_history.return_value = []
        self.addCleanup(self.get_history_patcher.stop)

    def init_get_interactions_patcher(self):
        self.get_interactions_patcher = patch("utils.api.resources.InteractionsResource.list")
        self.mock_get_interactions = self.get_interactions_patcher.start()
        self.mock_get_interactions.return_value = self.notes
        self.addCleanup(self.get_interactions_patcher.stop)

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
    def metadata_json(self):
        if self._metadata_json is None:
            self._metadata_json = open('core/fixtures/metadata.json').read()
        return self._metadata_json

    @property
    def barriers(self):
        if self._barriers is None:
            self._barriers = json.load(
                open('barriers/fixtures/barriers.json')
            )
        return self._barriers

    @property
    def barrier(self):
        return self.barriers[0]

    @property
    def assessments(self):
        if self._assessments is None:
            assessments = json.load(
                open('barriers/fixtures/assessments.json')
            )
            self._assessments = [
                Assessment(assessment) for assessment in assessments
            ]
        return self._assessments

    @property
    def notes(self):
        return [
            InteractionsResource.model({
                'id': 1,
                'kind': 'Comment',
                'text': 'Comment with document',
                'pinned': False,
                'is_active': True,
                'documents': [
                    {
                        'id': 'cd5ada56-53ee-4324-a2fa-b2f90f47ccbd',
                        'name': 'test.jpeg',
                        'size': 5159,
                        'status': 'virus_scanned'
                    },
                ],
                'created_on': '2020-01-20T12:00:00.683297Z',
                'created_by': {
                    'id': 1,
                    'name': 'Test-user'
                }
            }),
            InteractionsResource.model({
                'id': 2,
                'kind': 'Comment',
                'text': 'Comment without document',
                'pinned': False,
                'is_active': True,
                'documents': [],
                'created_on': '2020-01-21T09:30:00.714208Z',
                'created_by': {
                    'id': 1,
                    'name': 'Test-user'
                }
            }),
        ]
