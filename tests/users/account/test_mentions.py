from http import HTTPStatus
from unittest.mock import patch

from django.urls import reverse

from core.tests import MarketAccessTestCase
from utils.api.resources import UserMentionCountsResource


class MentionsTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.NotificationExclusionResource.get")
    @patch("utils.api.resources.MentionResource.list")
    @patch("utils.api.resources.UserMentionCountsResource.get")
    def test_user_can_access_mentions_page(self, mock_counts, mock_list, _):
        mock_counts.return_value = UserMentionCountsResource.model(
            {
                "read_by_recipient": 0,
                "total": 10,
            }
        )

        response = self.client.get(reverse("users:mentions"))

        mock_list.assert_called_once()
        assert mock_counts.call_count == 2
        assert response.status_code == HTTPStatus.OK

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.list")
    @patch("utils.api.resources.UserMentionCountsResource.get")
    def test_dashboard_no_mentions(self, mock_get, _, __):
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

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.list")
    @patch("utils.api.resources.NotificationExclusionResource.list")
    @patch("utils.api.resources.UserMentionCountsResource.get")
    def test_dashboard_has_mentions(self, mock_get, _, __, ___):
        mock_get.return_value = UserMentionCountsResource.model(
            {
                "read_by_recipient": 0,
                "total": 10,
            }
        )

        response = self.client.get(reverse("barriers:dashboard"))

        assert response.status_code == HTTPStatus.OK
        mock_get.assert_called_once()
        html = response.content.decode("utf8")
        assert "Mentions" in html
        assert (
            '<span class="govuk-tag ma-badge ma-badge--attention new-mention-count">10</span>'
            in html
        )
