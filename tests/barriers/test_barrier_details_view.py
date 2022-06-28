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


class BarrierViewOutstandingSectorsTestCase(MarketAccessTestCase):
    def test_barrier_view_shows_sectors_outstanding_if_no_sectors_specified(self):
        self.barrier["all_sectors"] = False
        self.barrier["sectors"] = []
        sectors_affected_url = reverse(
            "barriers:edit_sectors", kwargs={"barrier_id": self.barrier["id"]}
        )
        sectors_affected_link = f'<a href="{sectors_affected_url}">Sectors affected</a>'

        response = self.client.get(
            reverse(
                "barriers:barrier_detail", kwargs={"barrier_id": self.barrier["id"]}
            )
        )
        html = response.content.decode("utf8")

        assert sectors_affected_link in html

    def test_barrier_view_does_not_show_sectors_outstanding_if_a_sector_specified(self):
        # The default barrier has a sector. Let's hope that doesn't change.
        sectors_affected_url = reverse(
            "barriers:edit_sectors", kwargs={"barrier_id": self.barrier["id"]}
        )
        sectors_affected_link = f'<a href="{sectors_affected_url}">Sectors affected</a>'

        response = self.client.get(
            reverse(
                "barriers:barrier_detail", kwargs={"barrier_id": self.barrier["id"]}
            )
        )
        html = response.content.decode("utf8")

        assert sectors_affected_link not in html

    def test_barrier_view_does_not_show_sectors_outstanding_if_all_sectors_specified(
        self,
    ):
        self.barrier["all_sectors"] = True
        self.barrier["sectors"] = []
        sectors_affected_url = reverse(
            "barriers:edit_sectors", kwargs={"barrier_id": self.barrier["id"]}
        )
        sectors_affected_link = f'<a href="{sectors_affected_url}">Sectors affected</a>'

        response = self.client.get(
            reverse(
                "barriers:barrier_detail", kwargs={"barrier_id": self.barrier["id"]}
            )
        )
        html = response.content.decode("utf8")

        assert sectors_affected_link not in html
