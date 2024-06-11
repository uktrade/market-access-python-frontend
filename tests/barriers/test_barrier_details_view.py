from datetime import datetime, timezone
from http import HTTPStatus

from django.urls import reverse
from mock import patch

from barriers.models import HistoryItem
from core.tests import MarketAccessTestCase


class BarrierViewTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.BarriersResource.get_activity")
    def test_barrier_view_has_highlighted_event_list_items(self, mock_history):
        mock_history.return_value = [HistoryItem(result) for result in self.history]
        css_class = "event-list__item--unseen"
        expected_css_class_count = 2
        self.barrier["last_seen_on"] = str(
            datetime(2020, 3, 19, 12, 30, tzinfo=timezone.utc)
        )

        response = self.client.get(
            reverse(
                "barriers:barrier_detail", kwargs={"barrier_id": self.barrier["id"]}
            )
        )
        html = response.content.decode("utf8")

        assert HTTPStatus.OK == response.status_code
        unseen_events_count = html.count(css_class)
        assert (
            expected_css_class_count == unseen_events_count
        ), f"Expected {expected_css_class_count} unseen events, got: {unseen_events_count}"

    @patch("utils.api.resources.BarriersResource.get_activity")
    def test_barrier_view_without_highlighted_event_list_items(self, mock_history):
        mock_history.return_value = [HistoryItem(result) for result in self.history]
        css_class = "event-list__item--unseen"
        expected_css_class_count = 0
        self.barrier["last_seen_on"] = str(
            datetime(2020, 4, 19, 12, 30, tzinfo=timezone.utc)
        )

        response = self.client.get(
            reverse(
                "barriers:barrier_detail", kwargs={"barrier_id": self.barrier["id"]}
            )
        )
        html = response.content.decode("utf8")

        assert HTTPStatus.OK == response.status_code
        unseen_events_count = html.count(css_class)
        assert (
            expected_css_class_count == unseen_events_count
        ), f"Expected {expected_css_class_count} unseen events, got: {unseen_events_count}"

    @patch("utils.api.resources.BarriersResource.get_full_history")
    def test_barrier_full_history_list_items(self, mock_history):
        # History items found in tests/barriers/fixtures/history.json
        mock_history.return_value = [HistoryItem(result) for result in self.history]
        history_item_class = '"history-item"'
        response = self.client.get(
            reverse("barriers:history", kwargs={"barrier_id": self.barrier["id"]})
        )
        html = response.content.decode("utf8")
        assert HTTPStatus.OK == response.status_code
        # Currently expect 9 items in return, update count with more additions
        expected_history_item_count = 9
        displayed_history_items_count = html.count(history_item_class)
        assert expected_history_item_count == displayed_history_items_count

    @patch("utils.api.resources.BarriersResource.get_full_history")
    def test_barrier_history_list_top_priority_items(self, mock_history):
        # We expect 5 top priority items returned, but only 2 displayed
        # Only APPROVED and REMOVED should be displayed
        mock_history.return_value = [HistoryItem(result) for result in self.history]
        top_priority_history_item_class = (
            '<h4 class="history-item__field" tabindex="0">PB100 Priority Status</h4>'
        )
        response = self.client.get(
            reverse("barriers:history", kwargs={"barrier_id": self.barrier["id"]})
        )
        html = response.content.decode("utf8")

        # Check full history contains 5 top_priority_status updates
        history_changes_count = 0
        for item in self.history:
            if item["field"] == "top_priority_status":
                history_changes_count = history_changes_count + 1
        assert history_changes_count == 5

        # Check 5 are displayed
        assert HTTPStatus.OK == response.status_code
        expected_history_item_count = 5
        displayed_history_items_count = html.count(top_priority_history_item_class)
        assert expected_history_item_count == displayed_history_items_count
