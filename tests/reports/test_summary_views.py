from http import HTTPStatus

from django.urls import reverse, resolve
from mock import patch

from core.tests import ReportsTestCase
from reports.models import Report
from reports.views import NewReportBarrierSummaryView
from tests.constants import ERROR_HTML


class SummaryViewTestCase(ReportsTestCase):

    def setUp(self):
        super().setUp()
        self.draft = self.draft_barrier(5)
        self.url = reverse("reports:barrier_summary_uuid", kwargs={"barrier_id": self.draft["id"]})
        self.session_key = f'draft_barrier_{self.draft["id"]}_summary'

    def test_summary_url_resolves_to_correct_view(self):
        match = resolve(f'/reports/{self.draft["id"]}/summary/')
        assert match.func.view_class == NewReportBarrierSummaryView

    def test_summary_view_loads_correct_template(self):
        response = self.client.get(self.url)
        assert HTTPStatus.OK == response.status_code
        self.assertTemplateUsed(response, "reports/new_report_barrier_summary.html")

    def test_summary_view_returns_correct_html(self):
        expected_title = "<title>Market Access - Add - Barrier summary</title>"
        barrier_desc_textarea = '<textarea class="govuk-textarea js-character-count" id="description"'
        steps_textarea = '<textarea class="govuk-textarea" id="next-steps"'

        save_btn = '<input type="submit" value="Save and continue" class="govuk-button">'
        exit_btn = (
            '<button type="submit" class="govuk-button button--secondary" '
            'name="action" value="exit">Save and exit</button>'
        )

        response = self.client.get(self.url)
        html = response.content.decode('utf8')

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert barrier_desc_textarea in html
        assert steps_textarea in html
        assert save_btn in html
        assert exit_btn in html

    @patch("reports.helpers.ReportFormGroup.save")
    def test_summary_view_required_fields(self, mock_save):
        response = self.client.post(self.url, {})
        saved_form_data = self.client.session.get(self.session_key)
        html = response.content.decode("utf8")
        form = response.context["form"]

        assert HTTPStatus.OK == response.status_code
        assert form.is_valid() is False
        self.assertFormError(response, "form", "problem_description", "This field is required.")
        self.assertFormError(response, "form", "next_steps_summary", "This field is required.")
        assert ERROR_HTML.SUMMARY_HEADER in html
        assert ERROR_HTML.REQUIRED_FIELD in html
        assert saved_form_data is None
        assert mock_save.called is False

    @patch("utils.api.client.ReportsResource.get")
    @patch("reports.helpers.ReportFormGroup._update_barrier")
    def test_save_and_continue_redirects_to_correct_view(self, mock_update, mock_get):
        """
        Clicking on `Save and continue` button should update the draft barrier
        and redirect the user to the draft barrier details view
        """
        mock_update.return_value = Report(self.draft)
        mock_get.return_value = Report(self.draft)
        redirect_url = reverse("reports:draft_barrier_details_uuid", kwargs={"barrier_id": self.draft["id"]})
        data = {
            "problem_description": "wibble wobble",
            "next_steps_summary": "step 1 - wobble, step 2 - wibble",
        }

        response = self.client.post(self.url, data)

        self.assertRedirects(response, redirect_url)
        assert mock_update.called is True

    @patch("utils.api.client.ReportsResource.get")
    @patch("reports.helpers.ReportFormGroup._update_barrier")
    def test_button_save_and_exit_redirects_to_correct_view(self, mock_update, mock_get):
        """
        Clicking on `Save and exit` button should update the draft barrier
        and redirect the user to the draft barrier details view
        """
        mock_update.return_value = Report(self.draft)
        mock_get.return_value = Report(self.draft)
        redirect_url = reverse("reports:draft_barrier_details_uuid", kwargs={"barrier_id": self.draft["id"]})
        data = {
            "action": "exit",
            "problem_description": "wibble wobble",
            "next_steps_summary": "step 1 - wobble, step 2 - wibble",
        }

        response = self.client.post(self.url, data)

        self.assertRedirects(response, redirect_url)
        assert mock_update.called is True
