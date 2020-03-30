from datetime import datetime, timezone
from http import HTTPStatus

from django.urls import reverse
from mock import patch

from barriers.models import HistoryItem
from core.tests import MarketAccessTestCase


class BarrierViewTestCase(MarketAccessTestCase):

    @patch('utils.api.resources.BarriersResource.get_activity')
    def test_barrier_view_has_highlighted_event_list_items(self, mock_history):
        mock_history.return_value = [HistoryItem(result) for result in self.history]
        css_class = 'event-list__item--unseen'
        expected_css_class_count = 2
        self.barrier["last_seen_on"] = str(datetime(2020, 3, 19, 12, 30, tzinfo=timezone.utc))

        response = self.client.get(
            reverse("barriers:barrier_detail", kwargs={"barrier_id": self.barrier["id"]})
        )
        html = response.content.decode('utf8')

        assert HTTPStatus.OK == response.status_code
        unseen_events_count = html.count(css_class)
        assert expected_css_class_count == unseen_events_count, \
            f'Expected {expected_css_class_count} unseen events, got: {unseen_events_count}'

    @patch('utils.api.resources.BarriersResource.get_activity')
    def test_barrier_view_without_highlighted_event_list_items(self, mock_history):
        mock_history.return_value = [HistoryItem(result) for result in self.history]
        css_class = 'event-list__item--unseen'
        expected_css_class_count = 0
        self.barrier["last_seen_on"] = str(datetime(2020, 4, 19, 12, 30, tzinfo=timezone.utc))

        response = self.client.get(
            reverse("barriers:barrier_detail", kwargs={"barrier_id": self.barrier["id"]})
        )
        html = response.content.decode('utf8')

        assert HTTPStatus.OK == response.status_code
        unseen_events_count = html.count(css_class)
        assert expected_css_class_count == unseen_events_count, \
            f'Expected {expected_css_class_count} unseen events, got: {unseen_events_count}'
