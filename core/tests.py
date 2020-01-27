import json

from django.test import TestCase

from utils.api_client import BarriersResource

from mock import patch


class MarketAccessTestCase(TestCase):
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
        self.get_barrier_patcher = patch("utils.api_client.BarriersResource.get")
        self.mock_get_barrier = self.get_barrier_patcher.start()
        self.mock_get_barrier.return_value = BarriersResource.model(self.barriers[0])
        self.addCleanup(self.get_barrier_patcher.stop)

    def init_get_barrier_patcher(self):
        self.get_barrier_patcher = patch("utils.api_client.BarriersResource.get")
        self.mock_get_barrier = self.get_barrier_patcher.start()
        self.mock_get_barrier.return_value = BarriersResource.model(self.barriers[0])
        self.addCleanup(self.get_barrier_patcher.stop)

    def init_get_history_patcher(self):
        self.get_history_patcher = patch("utils.api_client.BarriersResource.get_history")
        self.mock_get_history = self.get_history_patcher.start()
        self.mock_get_history.return_value = []
        self.addCleanup(self.get_history_patcher.stop)

    def init_get_interactions_patcher(self):
        self.get_interactions_patcher = patch("utils.api_client.InteractionsResource.list")
        self.mock_get_interactions = self.get_interactions_patcher.start()
        self.mock_get_interactions.return_value = []
        self.addCleanup(self.get_interactions_patcher.stop)

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
