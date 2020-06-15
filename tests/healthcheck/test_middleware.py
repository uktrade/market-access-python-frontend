from unittest.mock import Mock

from django.test import TestCase

from healthcheck.middleware import StatsMiddleware


class TestMiddleware(TestCase):

    """
    Test Healthcheck Middleware
    """

    def setUp(self):
        get_response = Mock()
        self.middleware = StatsMiddleware()
        self.request = Mock(spec=[""])

    def test_middleware_start_time_added(self):
        """ Checks start_time is added to a request object in middleware"""
        self.assertFalse(hasattr(self.request, "start_time"))
        self.middleware.process_request(self.request)
        self.assertTrue(hasattr(self.request, "start_time"))
