from http import HTTPStatus
from unittest.mock import patch

from django.urls import reverse

from core.tests import MarketAccessTestCase
from utils.api.resources import UserMentionCountsResource


class MentionsTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.list")
    def test_user_can_access_mentions_page(self, *args):
        response = self.client.get(reverse("users:mentions"))
        assert response.status_code == HTTPStatus.OK
        assert 0

    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.list")
    def test_dashboard_no_mentions(self, *args):
        response = self.client.get(reverse("barriers:dashboard"))
        assert response.status_code == HTTPStatus.OK
        html = response.content.decode("utf8")
        assert "Mentions" in html
        assert "govuk-tag ma-badge ma-badge--attention new-mention-count" not in html
        assert 0

    @patch("utils.api.resources.UserMentionCountsResource.get")
    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.list")
    def test_dashboard_has_mentions(self, mock, *args):
        mock.return_value = UserMentionCountsResource.model(
            {
                "read_by_recipient": 0,
                "total": 10,
            }
        )
        response = self.client.get(reverse("barriers:dashboard"))
        assert response.status_code == HTTPStatus.OK
        html = response.content.decode("utf8")
        assert mock.call_count == 1
        assert "Mentions" in html
        assert (
            '<span class="govuk-tag ma-badge ma-badge--attention new-mention-count">10</span>'
            in html
        )
        assert 0
