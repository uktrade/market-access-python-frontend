from http import HTTPStatus
from unittest.mock import Mock, patch

from django.urls import reverse

from core.tests import MarketAccessTestCase


class FeedbackTestCase(MarketAccessTestCase):
    """
    Test the Feedback process
    """

    @patch("utils.api.resources.FeedbackResource.send_feedback")
    def test_feedback_requires_satisfaction_level(
        self, mock_send_feedback_method: Mock
    ):
        mock_send_feedback_method.return_value = {}
        url = reverse(
            "core:feedback",
        )
        response = self.client.post(
            url,
            follow=False,
            data={},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert "satisfaction" in form.errors

    @patch("utils.api.resources.FeedbackResource.send_feedback")
    def test_feedback_requires_attempted_action(self, mock_send_feedback_method: Mock):
        mock_send_feedback_method.return_value = {}
        url = reverse(
            "core:feedback",
        )
        response = self.client.post(
            url,
            follow=False,
            data={},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert "attempted_actions" in form.errors
