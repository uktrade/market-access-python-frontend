# CASES TO TEST #

# 3. Resuming a draft loads data into session correctly.

import logging
from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase
from mock import patch
from reports.report_barrier_view import ReportBarrierWizardView

logger = logging.getLogger(__name__)


class NewReportTestCase(MarketAccessTestCase):
    # Test suite for starting new barriers
    # make django-test path=reports/test_wizard_start_new_and_resume_draft.py::NewReportTestCase

    def test_new_report_page_loads(self):
        # Test the new report endpoint responds
        response = self.client.get(reverse("reports:new_report"))
        # Check correct template loaded
        assert response.status_code == HTTPStatus.OK
        assert "reports/new_report.html" in response.template_name

    def test_new_report_start_new_barrier(self):
        # Submitting "start now" loads about form with clean session data
        response = self.client.get(
            reverse("reports:report-barrier-wizard") + "?reset=true", follow=True
        )

        assert response.status_code == HTTPStatus.OK
        assert "reports/barrier_about_wizard_step.html" in response.template_name
        assert "form" in response.context
        assert response.context["form"].initial == {}

    def test_page_routes(self):
        form_page_names = [
            "barrier-about",
            "barrier-status",
            "barrier-location",
            "barrier-trade-direction",
            "barrier-sectors-affected",
            "barrier-companies-affected",
            "barrier-export-type",
            "barrier-details-summary",
        ]

        for page_name in form_page_names:

            response = self.client.get(
                reverse("reports:report-barrier-wizard-step", kwargs={"step": page_name}), follow=True
            )

            template_name = page_name.replace("-", "_")
            assert response.status_code == HTTPStatus.OK
            assert f"reports/{template_name}_wizard_step.html" in response.template_name
            assert "form" in response.context
            assert response.context["form"].initial == {}

    @patch("reports.report_barrier_view.ReportBarrierWizardView.save_report_progress")
    def test_save_and_quit(self, mock_save):
        response = self.client.get(
            reverse("reports:report-barrier-wizard-step", kwargs={"step": "skip"}), follow=True
        )

        assert response.status_code == HTTPStatus.OK
        mock_save.assert_called()
        assert "barriers/dashboard.html" in response.template_name


class DraftReportTestCase(MarketAccessTestCase):
    # Test suite for resuming a saved draft barrier
    # make django-test path=reports/test_wizard_start_new_and_resume_draft.py::DraftReportTestCase

    #@patch("utils.api.resources.ReportsResource.get")
    #def test_new_report_start_draft_barrier(self, mock_get_reports):
    def test_new_report_start_draft_barrier(self):
        # Resuming a draft barrier redirects user to stored step and repopulates session data

        # Create a barrier, fill in some information for new_report_session_data and is_draft = true
        # use that id and test that the right step is loaded.

        logger.critical(self.barriers[4])

        #mock_get_reports.return_value = self.barriers[4]

        response = self.client.get(
            reverse(
                "reports:report-barrier-drafts",
                kwargs={"draft_barrier_id": self.barriers[4]["id"]},
            )
        )

        


        assert response.status_code == HTTPStatus.OK
        assert "reports/barrier_about_wizard_step.html" in response.template_name
        assert "form" in response.context
        assert response.context["form"].initial == {}


        #{
        #    'data': {
        #        'admin_areas': [], 
        #        'all_sectors': None, 
        #        'caused_by_trading_bloc': None, 
        #        'code': 'B-23-XUT', 
        #        'country': None, 
        #        'created_by': {'id': 45, 'name': 'Your'}, 
        #        'created_on': '2023-07-21T14:20:00.974045Z', 
        #        'id': '684547bb-5cab-4b04-80f6-cdea19c8e6a0', 
        #        'is_summary_sensitive': None, 
        #        'is_top_priority': False, 
        #        'location': '', 
        #        'modified_by': {'id': 45, 'name': 'Your'}, 
        #        'modified_on': '2023-07-21T14:20:25.401148Z', 
        #        'next_steps_summary': '', 
        #        'other_source': '', 
        #        'product': '', 
        #        'progress': [{
        #            'stage_code': '1.1', 
        #            'stage_desc': 'Barrier status', 
        #            'status_id': 1, 
        #            'status_desc': 'NOT STARTED'
        #            }, {
        #            'stage_code': '1.2', 
        #            'stage_desc': 'Location of the barrier', 
        #            'status_id': 1, 
        #            'status_desc': 'NOT STARTED'
        #            }, {
        #            'stage_code': '1.3', 
        #            'stage_desc': 'Sectors affected by the barrier', 
        #            'status_id': 1, 
        #            'status_desc': 'NOT STARTED'
        #            }, {
        #            'stage_code': '1.4', 
        #            'stage_desc': 'About the barrier', 
        #            'status_id': 2, 
        #            'status_desc': 'IN PROGRESS'
        #            }, {
        #            'stage_code': '1.5', 
        #            'stage_desc': 'Barrier summary', 
        #            'status_id': 3, 
        #            'status_desc': 'COMPLETED'
        #        }], 
        #        'sectors': [], 
        #        'main_sector': None, 
        #        'sectors_affected': None, 
        #        'source': {'code': '', 'name': 'Unknown'}, 
        #        'status': {'id': 0, 'name': 'Unfinished'}, 
        #        'status_date': None, 
        #        'status_summary': '', 
        #        'sub_status': {'code': '', 'name': None}, 
        #        'sub_status_other': '', 
        #        'summary': 'yttyjt', 
        #        'tags': [], 
        #        'term': None, 
        #        'title': 'ytjtuyj', 
        #        'trade_direction': None, 
        #        'trading_bloc': None, 
        #        'categories': [], 
        #        'commodities': [], 
        #        'draft': True, 
        #        'caused_by_admin_areas': None, 
        #        'new_report_session_data': '{
        #            "step": "barrier-status", 
        #            "step_data": {
        #                "barrier-about": {
        #                    "csrfmiddlewaretoken": ["oLT6pJrRRAipoRg4r3mhCkKqt7XV2FFfoidcMVoPwMAZOydbEw8ntkd5u8ZJ9qbK"], 
        #                    "report_barrier_wizard_view-current_step": ["barrier-about"], 
        #                    "barrier-about-title": ["ytjtuyj"], 
        #                    "barrier-about-summary": ["yttyjt"]
        #                }
        #            }, 
        #            "step_files": {
        #                "barrier-about": {}
        #            }, 
        #            "extra_data": {}, 
        #            "meta": {"barrier_id": "684547bb-5cab-4b04-80f6-cdea19c8e6a0"}
        #        }', 
        #        'companies': None, 
        #        'related_organisations': None, 
        #        'start_date': None, 
        #        'is_start_date_known': False, 
        #        'is_currently_active': None, 
        #        'export_types': [], 
        #        'export_description': None
        #    }
        #}

        #self.get_barrier_patcher = patch("utils.api.resources.BarriersResource.get")
        #self.mock_get_barrier = self.get_barrier_patcher.start()
        #self.mock_get_barrier.return_value = BarriersResource.model(
        #    self.barriers[self.barrier_index]
        #)