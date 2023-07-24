import logging
from http import HTTPStatus

from django.urls import reverse
from mock import patch

from core.tests import MarketAccessTestCase

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
                reverse(
                    "reports:report-barrier-wizard-step", kwargs={"step": page_name}
                ),
                follow=True,
            )

            template_name = page_name.replace("-", "_")
            assert response.status_code == HTTPStatus.OK
            assert f"reports/{template_name}_wizard_step.html" in response.template_name
            assert "form" in response.context
            assert response.context["form"].initial == {}

    @patch("reports.report_barrier_view.ReportBarrierWizardView.save_report_progress")
    def test_save_and_quit(self, mock_save):
        response = self.client.get(
            reverse("reports:report-barrier-wizard-step", kwargs={"step": "skip"}),
            follow=True,
        )

        assert response.status_code == HTTPStatus.OK
        mock_save.assert_called()
        assert "barriers/dashboard.html" in response.template_name


class DraftReportTestCase(MarketAccessTestCase):
    # Test suite for resuming a saved draft barrier
    # make django-test path=reports/test_wizard_start_new_and_resume_draft.py::DraftReportTestCase

    @patch("reports.report_barrier_view.ReportBarrierWizardView.save_report_progress")
    def test_new_report_resume_draft_barrier(self, save_patch):
        # Resuming a draft barrier redirects user to stored step and repopulates session data
        response = self.client.get(
            reverse(
                "reports:report-barrier-drafts",
                kwargs={"draft_barrier_id": self.draft_barrier["id"]},
            ),
            follow=True,
        )

        # Report data from reports/fixtures/draft_barriers.json - has about step
        # complete, so expect redirect to status step.
        assert response.status_code == HTTPStatus.OK
        assert "reports/barrier_status_wizard_step.html" in response.template_name
        assert "form" in response.context
        assert response.context["form"].initial == {}
