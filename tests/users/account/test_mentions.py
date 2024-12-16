import json
from http import HTTPStatus
from unittest.mock import patch

from django.urls import reverse

from barriers.models.history.mentions import Mention
from core.tests import MarketAccessTestCase


class MentionsTestCase(MarketAccessTestCase):

    def test_user_can_access_mentions(self):
        response = self.client.get(reverse("users:mentions"))
        assert response.status_code != HTTPStatus.OK

    # def test_user_gets_mention_notifications(self):
    #     print('HELLO')
    #     response = self.client.get(reverse("barriers:dashboard"))
    #     assert response.status_code == HTTPStatus.OK
    #     html = response.content.decode("utf8")
    #     assert "Mentions" in html
    #     assert 2 == 0
    #     assert '<span class="govuk-tag ma-badge ma-badge--attention new-mention-count">1</span>' in html

