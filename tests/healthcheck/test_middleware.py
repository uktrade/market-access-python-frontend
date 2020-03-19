from unittest.mock import Mock

from django.test import TestCase

from healthcheck.middleware import HealthCheckMiddleware


class TestMiddleware(TestCase):

    """
    Test Healthcheck Middleware
    """

    def setUp(self):
        get_response = Mock()
        self.middleware = HealthCheckMiddleware(get_response)
        self.request = Mock(spec=[""])

    def test_middleware_start_time_added(self):
        """ Checks start_time is added to a request object in middleware"""
        self.assertFalse(hasattr(self.request, "start_time"))
        self.middleware(self.request)
        self.assertTrue(hasattr(self.request, "start_time"))
