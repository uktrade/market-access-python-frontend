import json
import os

from django.conf import settings
from django.urls import reverse
from mock import patch

from core.tests import MarketAccessTestCase, ReportsTestsMixin
from reports.models import Report
from utils.api.client import MarketAccessAPIClient


def save_barrier_snapshot(response, name):

    barrier = response.context_data["barrier"].data
    snapshot_path = os.path.join(
        settings.BASE_DIR, "../tests/reports/fixtures/", f"{name}.json"
    )
    with open(snapshot_path, "w") as f:
        json.dump(barrier, f)
    return


class TestReportBarrierJourney(ReportsTestsMixin, MarketAccessTestCase):

    new_report_url = "reports:new_report"
    new_report_start_url = "reports:barrier_start"
    new_report_about_url = "reports:barrier_about_uuid"
    new_report_status_url = "reports:barrier_status_uuid"
    new_report_location_url = "reports:barrier_location_uuid"
    new_report_trade_direction_url = "reports:barrier_trade_direction_uuid"
    new_report_has_sectors_url = "reports:barrier_has_sectors_uuid"
    new_report_sectors_url = "reports:barrier_sectors_uuid"
    barrier_categories_add_first_uuid = "reports:barrier_categories_add_first_uuid"
    new_report_categories_url = "reports:barrier_categories_uuid"
    new_report_commodities_url = "reports:barrier_commodities_uuid"
    new_report_check_answers_url = "reports:barrier_check_answers_uuid"
    new_report_final_barrier_url = "barriers:barrier_detail_from_complete"

    def from_snapshot(self, name):
        snapshot_path = os.path.join(
            settings.BASE_DIR, "../tests/reports/fixtures/", f"{name}.json"
        )
        with open(snapshot_path, "r") as f:
            return json.load(f)

    def assertBarrierEqual(self, response, snapshot_name):
        barrier = response.context_data["barrier"].data
        snapshot = self.from_snapshot(snapshot_name)
        assert barrier == snapshot

    def test_api_usage(self):
        client = MarketAccessAPIClient()
        client.token = "iluQNpB9Ac5ft2GBKyE8y6KNBSQdwI"
        reports = client.reports.list()
        assert len(reports) == 10

    # @patch("utils.api.resources.APIResource.create")
    # @patch("utils.api.resources.APIResource.get")
    def test_start_report_journey(self):
        start_url = reverse(self.new_report_url)
        response = self.client.get(start_url, follow=True)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf8")

        # is CTA displayed on page
        next_url = reverse(self.new_report_start_url)
        assert f'href="{next_url}' in html

        # is CTA redirecting to correct page
        # mock_get.return_value = Report(self.draft_barriers[0])
        # mock_create.return_value = Report(self.draft_barriers[0])

        response = self.client.get(next_url, follow=True)
        barrier = response.context_data["barrier"]
        save_barrier_snapshot(response, "report_barrier_start")

        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf8")
        assert f'href="{start_url}' in html

        # assert that form is in response context
        form = response.context_data["form"]
        assert form.is_valid() is False
        assert form.errors == {}

        submit_form_data = {
            "title": "Test barrier about Marshmallows",
            "product": "Test product",
            "source": "COMPANY",
            "other_source": "",
            "summary": "Test summary",
            "is_summary_sensitive": "False",
            "action": "save-and-continue",
        }

        about_form_url = reverse(
            self.new_report_about_url, kwargs={"barrier_id": barrier.id}
        )

        # submit form data to page
        response = self.client.post(about_form_url, submit_form_data, follow=True)
        save_barrier_snapshot(response, "report_barrier_about")
        self.assertBarrierEqual(response, "report_barrier_about")

        # check that user is redirected to correct page
        self.assertEqual(response.status_code, 200)
        barrier_status_url = reverse(
            self.new_report_status_url, kwargs={"barrier_id": barrier.id}
        )
        self.assertRedirects(response, barrier_status_url)

        submit_form_data = {
            "term": 2,
            "status": 2,
            "open_in_progress_summary": "asdasdasd",
            "action": "save-and-continue",
        }

        response = self.client.post(barrier_status_url, submit_form_data, follow=True)
        save_barrier_snapshot(response, "report_barrier_status")
        self.assertBarrierEqual(response, "report_barrier_status")

        # check that user is redirected to correct page
        self.assertEqual(response.status_code, 200)
        barrier_location_url = reverse(
            self.new_report_location_url, kwargs={"barrier_id": barrier.id}
        )
        self.assertRedirects(response, barrier_location_url)

        submit_form_data = {
            "location": "81756b9a-5d95-e211-a939-e4115bead28a",
            "has_admin_areas": 2,
            "admin_areas": "a88512e0-62d4-4808-95dc-d3beab05d0e9",
            "action": "save-and-continue",
        }

        response = self.client.post(barrier_location_url, submit_form_data, follow=True)
        save_barrier_snapshot(response, "report_barrier_location")
        self.assertBarrierEqual(response, "report_barrier_location")

        # check that user is redirected to correct page
        self.assertEqual(response.status_code, 200)
        barrier_trade_direction_url = reverse(
            self.new_report_trade_direction_url,
            kwargs={"barrier_id": barrier.id},
        )
        self.assertRedirects(response, barrier_trade_direction_url)

        submit_form_data = {
            "trade_direction": 2,
            "action": "save-and-continue",
        }

        response = self.client.post(
            barrier_trade_direction_url, submit_form_data, follow=True
        )
        save_barrier_snapshot(response, "report_barrier_trade_direction")
        self.assertBarrierEqual(response, "report_barrier_trade_direction")

        # check that user is redirected to correct page
        self.assertEqual(response.status_code, 200)
        barrier_has_sectors_url = reverse(
            self.new_report_has_sectors_url, kwargs={"barrier_id": barrier.id}
        )
        self.assertRedirects(response, barrier_has_sectors_url)

        submit_form_data = {"sectors_affected": 1}

        response = self.client.post(
            barrier_has_sectors_url, submit_form_data, follow=True
        )
        save_barrier_snapshot(response, "report_barrier_has_sectors")
        self.assertBarrierEqual(response, "report_barrier_has_sectors")

        # check that user is redirected to correct page
        self.assertEqual(response.status_code, 200)
        barrier_sectors_url = reverse(
            self.new_report_sectors_url, kwargs={"barrier_id": barrier.id}
        )
        self.assertRedirects(response, barrier_sectors_url)

        submit_form_data = {
            "sectors": "9f38cecc-5f95-e211-a939-e4115bead28a",
            "action": "continue",
        }

        response = self.client.post(barrier_sectors_url, submit_form_data, follow=True)
        save_barrier_snapshot(response, "report_barrier_sectors")
        self.assertBarrierEqual(response, "report_barrier_sectors")

        # check that user is redirected to correct page
        self.assertEqual(response.status_code, 200)
        barrier_add_category_url = reverse(
            self.barrier_categories_add_first_uuid, kwargs={"barrier_id": barrier.id}
        )
        self.assertRedirects(response, barrier_add_category_url)

        submit_form_data = {
            "category": "129",
            "action": "save-and-continue",
        }

        response = self.client.post(
            barrier_add_category_url, submit_form_data, follow=True
        )
        save_barrier_snapshot(response, "report_barrier_add_category")
        self.assertBarrierEqual(response, "report_barrier_add_category")

        # check that user is redirected to correct page
        self.assertEqual(response.status_code, 200)
        barrier_categories_url = reverse(
            self.new_report_categories_url, kwargs={"barrier_id": barrier.id}
        )
        self.assertRedirects(response, barrier_categories_url)

        submit_form_data = {
            "categories": "129",
            "action": "save-and-continue",
        }

        response = self.client.post(
            barrier_categories_url, submit_form_data, follow=True
        )
        save_barrier_snapshot(response, "report_barrier_categories")
        self.assertBarrierEqual(response, "report_barrier_categories")

        # check that user is redirected to correct page
        self.assertEqual(response.status_code, 200)
        barrier_commodities_url = reverse(
            self.new_report_commodities_url, kwargs={"barrier_id": barrier.id}
        )
        self.assertRedirects(response, barrier_commodities_url)

        submit_form_data = {
            "codes": "1200000000",
            "countries": "81756b9a-5d95-e211-a939-e4115bead28a",
            "trading_blocs": "",
            "action": "save",
        }

        response = self.client.post(
            barrier_commodities_url, submit_form_data, follow=True
        )
        save_barrier_snapshot(response, "report_barrier_commodities")
        self.assertBarrierEqual(response, "report_barrier_commodities")
