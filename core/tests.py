import json

from django.test import TestCase

from mock import patch


class MarketAccessTestCase(TestCase):
    _barriers = None
    _metadata_json = None

    def setUp(self):
        self.init_session()
        self.init_metadata_patcher()
        self.init_get_barrier()

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

    def init_get_barrier(self):
        self.get_barrier_patcher = patch("utils.api_client.BarriersResource.get")
        from utils.api_client import BarriersResource
        self.mock_get_barrier = self.get_barrier_patcher.start()
        self.mock_get_barrier.return_value = BarriersResource.model(self.barriers[0])
        self.addCleanup(self.get_barrier_patcher.stop)

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
