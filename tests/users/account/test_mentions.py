import json
from http import HTTPStatus
from unittest.mock import patch

from django.urls import reverse

from core.tests import MarketAccessTestCase


class MentionsTestCase(MarketAccessTestCase):

    mention = {
        "barrier":"1",
        "email_used":"example@test.com",
        "recipient":"test user",
        "created_by_id":"2",
    }

    def user_id(self):
        return str(self.current_user.data["id"])

    def test_user_gets_mention_notifications(self):
        response = self.client.get(reverse("barriers:dashboard"))
        assert response.status_code == HTTPStatus.OK
        html = response.content.decode("utf8")
        print(html)
        print(self.mock_get_mentions().data["email_used"])
        assert "Mentions" in html
        assert '<span class="govuk-tag ma-badge ma-badge--attention new-mention-count">1</span>' in html
        

        print(self.user_id)
        print(self.mention.data['barrier'])
        print(self.mention.data['email_used'])
        assert 2 == 0
