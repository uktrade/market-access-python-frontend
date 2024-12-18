from http import HTTPStatus
from unittest.mock import patch

from django.urls import reverse

from core.tests import MarketAccessTestCase


class MentionsTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.MentionResource.list")
    @patch("utils.api.resources.NotificationExclusionResource.get")
    def test_user_can_access_mentions(self, mock_get, mock_mention_list):
        response = self.client.get(reverse("users:mentions"))

        assert response.status_code == HTTPStatus.OK
        mock_get.assert_called_once_with()
        assert mock_mention_list.call_count == 4

    @patch("utils.api.resources.APIResource.list")
    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.MentionResource.list")
    def test_dashboard_no_mentions(self, mock_list, *args):
        mock_list.return_value = []
        response = self.client.get(reverse("barriers:dashboard"))
        assert response.status_code == HTTPStatus.OK
        html = response.content.decode("utf8")
        assert mock_list.call_count == 2
        assert "Mentions" in html
        assert 'govuk-tag ma-badge ma-badge--attention new-mention-count' not in html

    @patch("utils.api.resources.APIResource.list")
    @patch("utils.api.resources.APIResource.get")
    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.MentionResource.list")
    def test_dashboard_has_mentions(self, mock_list, *args):
        mock_list.return_value = self.mentions
        response = self.client.get(reverse("barriers:dashboard"))
        assert response.status_code == HTTPStatus.OK
        html = response.content.decode("utf8")
        assert mock_list.call_count == 2
        assert "Mentions" in html
        assert f'<span class="govuk-tag ma-badge ma-badge--attention new-mention-count">{len(self.mentions)}</span>' in html
