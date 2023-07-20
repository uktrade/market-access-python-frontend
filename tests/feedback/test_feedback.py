import logging
import uuid
from http import HTTPStatus
from unittest.mock import Mock, patch

from django.urls import reverse

from core.tests import MarketAccessTestCase

logger = logging.getLogger(__name__)


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
            data={"csat_submission": "False"},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert "satisfaction" in form.errors

    @patch("utils.api.resources.FeedbackResource.send_feedback")
    def test_csat_redirect_does_not_require_satisfaction_level(
        self, mock_send_feedback_method: Mock
    ):
        mock_send_feedback_method.return_value = {
            "id": str(uuid.uuid4())
        }
        url = reverse(
            "core:feedback",
        )
        response = self.client.post(
            url,
            follow=False,
            data={"csat_submission": "True"},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert "satisfaction" not in form.errors

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
