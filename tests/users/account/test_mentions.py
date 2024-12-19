from http import HTTPStatus
from unittest.mock import patch

from django.urls import reverse

from core.tests import MarketAccessTestCase
from utils.api.resources import UserMentionCountsResource


class MentionsTestCase(MarketAccessTestCase):
    def test_user_can_access_mentions_page(self):
        response = self.client.get(reverse("users:mentions"))
        assert response.status_code == HTTPStatus.OK

    @patch("utils.api.resources.UserMentionCountsResource.get")
    def test_dashboard_no_mentions(self, mock_get):
        mock_get.return_value = UserMentionCountsResource.model(
            {
                "read_by_recipient": 0,
                "total": 0,
            }
        )
        response = self.client.get(reverse("barriers:dashboard"))
        assert response.status_code == HTTPStatus.OK
        mock_get.assert_called_once()
        html = response.content.decode("utf8")
        assert "Mentions" in html
        assert "govuk-tag ma-badge ma-badge--attention new-mention-count" not in html

    @patch("utils.api.resources.UserMentionCountsResource.get")
    def test_dashboard_has_mentions(self, mock_get):
        mock_get.return_value = UserMentionCountsResource.model(
            {
                "read_by_recipient": 0,
                "total": 10,
            }
        )
        response = self.client.get(reverse("barriers:dashboard"))
        assert response.status_code == HTTPStatus.OK
        html = response.content.decode("utf8")
        mock_get.assert_called_once()
        assert "Mentions" in html
        assert (
            '<span class="govuk-tag ma-badge ma-badge--attention new-mention-count">10</span>'
            in html
        )
