# CASES TO TEST #
#
# 1. Navigating to new report URL loads the correct page
#
# 2. Request triggered through clicking the start button
#    loads a new clean barrier, not an existing one from session.
#    Ensure current barrier in session is saved and wiped.
#
# 3. Resuming a draft loads data into session correctly.

import logging
from http import HTTPStatus

from django.urls import reverse

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


class DraftReportTestCase(MarketAccessTestCase):
    # Test suite for resuming a saved draft barrier
    # make django-test path=reports/test_wizard_start_new_and_resume_draft.py::DraftReportTestCase

    def test_new_report_start_draft_barrier(self):
        # Resuming a draft barrier redirects user to stored step and repopulates session data

        # Create a barrier, fill in some information for new_report_session_data and is_draft = true
        # use that id and test that the right step is loaded.

        response = self.client.get(
            reverse(
                "reports:report-barrier-drafts",
                kwargs={"draft_barrier_id": self.barrier["id"]},
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "reports/barrier_about_wizard_step.html" in response.template_name
        assert "form" in response.context
        assert response.context["form"].initial == {}
