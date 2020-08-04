from http import HTTPStatus

from django.urls import reverse, resolve
from mock import patch

from core.tests import ReportsTestCase
from reports.models import Report
from reports.views import NewReportBarrierAboutView
from tests.constants import ERROR_HTML


class AboutViewTestCase(ReportsTestCase):

    def setUp(self):
        super().setUp()
        self.draft = self.draft_barrier(4)
        self.url = reverse('reports:barrier_about_uuid', kwargs={"barrier_id": self.draft["id"]})
        self.session_key = f'draft_barrier_{self.draft["id"]}_about'

    def test_about_url_resolves_to_correct_view(self):
        match = resolve(f'/reports/{self.draft["id"]}/problem/')
        assert match.func.view_class == NewReportBarrierAboutView

    def test_about_view_loads_correct_template(self):
        response = self.client.get(self.url)
        assert HTTPStatus.OK == response.status_code
        self.assertTemplateUsed(response, 'reports/new_report_barrier_about.html')

    def test_about_view_returns_correct_html(self):
        expected_title = '<title>Market Access - Add - About the barrier</title>'
        name_input_field = '<input class="govuk-input" id="title"'
        product_input_field = '<input class="govuk-input" id="product"'
        barrier_source_radio_container = (
            '<div class="govuk-radios barrier-source govuk-radios--conditional" data-module="radios">'
        )
        barrier_source_radio_item = '<div class="govuk-radios__item barrier-source">'
        expected_barrier_source_radio_count = 4
        tags_container = '<div class="govuk-checkboxes" id="tags">'
        expected_save_btn = '<input type="submit" value="Save and continue" class="govuk-button">'
        expected_exit_btn = (
            '<button type="submit" class="govuk-button button--secondary" '
            'name="action" value="exit">Save and exit</button>'
        )

        response = self.client.get(self.url)
        html = response.content.decode('utf8')

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert name_input_field in html
        assert product_input_field in html
        assert barrier_source_radio_container in html
        assert tags_container in html
        # Barrier source radios
        bs_options_count = html.count(barrier_source_radio_item)
        assert expected_barrier_source_radio_count == bs_options_count, \
            f'Expected {expected_barrier_source_radio_count} barrier source radio buttons, got: {bs_options_count}'
        # Main Buttons
        assert expected_save_btn in html
        assert expected_exit_btn in html

    @patch("reports.helpers.ReportFormGroup.save")
    def test_about_view_required_fields(self, mock_save):
        response = self.client.post(self.url, {})
        saved_form_data = self.client.session.get(self.session_key)
        html = response.content.decode('utf8')
        form = response.context['form']

        assert HTTPStatus.OK == response.status_code
        assert form.is_valid() is False
        self.assertFormError(response, 'form', 'title', "Enter a name for this barrier")
        self.assertFormError(response, 'form', 'product', "Enter a product, service or investment")
        self.assertFormError(response, 'form', 'source', "Select how you became aware of the barrier")
        assert ERROR_HTML.SUMMARY_HEADER in html
        assert ERROR_HTML.REQUIRED_FIELD in html
        assert saved_form_data is None
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup._update_barrier")
    def test_save_and_continue_redirects_to_correct_view(self, mock_update):
        """
        Clicking on `Save and continue` should take the user to the .../summary/ page
        """
        mock_update.return_value = Report(self.draft)
        redirect_url = reverse('reports:barrier_summary_uuid', kwargs={"barrier_id": self.draft["id"]})
        data = {
            "title": "wibble",
            "product": "wobble",
            "source": "COMPANY",
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
        redirect_url = reverse('reports:draft_barrier_details_uuid', kwargs={"barrier_id": self.draft["id"]})
        data = {
            "action": "exit",
            "title": "wibble",
            "product": "wobble",
            "source": "COMPANY",
        }

        response = self.client.post(self.url, data)

        self.assertRedirects(response, redirect_url)
        assert mock_update.called is True
