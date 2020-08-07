from http import HTTPStatus

from django.urls import reverse, resolve
from mock import patch

from core.tests import MarketAccessTestCase
from reports.views import (
    NewReportBarrierTermView,
    NewReportBarrierStatusView,
)
from tests.constants import ERROR_HTML


class TermViewTestCase(MarketAccessTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('reports:barrier_term')

    def test_start_url_resolves_to_term_view(self):
        match = resolve('/reports/new/start/')
        assert match.func.view_class == NewReportBarrierTermView

    def test_term_view_returns_correct_html(self):
        expected_title = '<title>Market Access - Add - Barrier status</title>'
        expected_radio_container = '<div class="govuk-radios term">'
        radio_item = '<div class="govuk-radios__item">'
        expected_radio_count = 2
        expected_continue_btn = '<input type="submit" value="Continue" class="govuk-button">'

        response = self.client.get(self.url)
        html = response.content.decode('utf8')

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert expected_radio_container in html
        radio_count = html.count(radio_item)
        assert expected_radio_count is radio_count, f'Expected {expected_radio_count} radio items, got: {radio_count}'
        assert expected_continue_btn in html

    @patch("reports.helpers.ReportFormGroup.save")
    def test_term_cannot_be_empty(self, mock_save):
        field_name = 'term'
        session_key = 'draft_barrier__term_form_data'

        response = self.client.post(self.url, data={field_name: ''})
        saved_form_data = self.client.session.get(session_key)
        html = response.content.decode('utf8')
        form = response.context['form']

        assert HTTPStatus.OK == response.status_code
        assert form.is_valid() is False
        assert field_name in form.errors
        assert ERROR_HTML.SUMMARY_HEADER in html
        assert ERROR_HTML.REQUIRED_FIELD in html
        assert saved_form_data is None
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_term_saved_in_session(self, mock_save):
        field_name = 'term'
        session_key = 'draft_barrier__term_form_data'
        expected_form_data = {'term': '1'}

        response = self.client.post(self.url, data={field_name: '1'}, follow=True)
        saved_form_data = self.client.session.get(session_key)

        assert HTTPStatus.OK == response.status_code
        assert expected_form_data == saved_form_data
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_success_redirects_to_correct_view(self, mock_save):
        field_name = 'term'
        redirect_url = reverse('reports:barrier_status')

        response = self.client.post(self.url, data={field_name: '1'})

        self.assertRedirects(response, redirect_url)
        assert mock_save.called is False


class StatusViewTestCase(MarketAccessTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('reports:barrier_status')

    def test_isresolved_url_resolves_to_status_view(self):
        match = resolve('/reports/new/start/is-resolved/')
        assert match.func.view_class == NewReportBarrierStatusView

    def test_status_view_returns_correct_html(self):
        expected_title = '<title>Market Access - Add - Barrier status</title>'
        expected_radio_container = '<div class="govuk-radios status govuk-radios--conditional" '\
                                   'data-module="radios">'
        radio_item = '<div class="govuk-radios__item">'
        expected_radio_count = 9
        expected_continue_btn = '<input type="submit" class="govuk-button" value="Continue">'

        response = self.client.get(self.url)
        html = response.content.decode('utf8')

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert expected_radio_container in html
        radio_count = html.count(radio_item)
        assert expected_radio_count is radio_count, f'Expected {expected_radio_count} radio items, got: {radio_count}'
        assert expected_continue_btn in html

    @patch("reports.helpers.ReportFormGroup.save")
    def test_status_cannot_be_empty(self, mock_save):
        field_name = 'status'

        response = self.client.post(self.url, data={field_name: ''})
        html = response.content.decode('utf8')
        form = response.context['form']

        assert HTTPStatus.OK == response.status_code
        assert form.is_valid() is False
        assert field_name in form.errors
        assert ERROR_HTML.SUMMARY_HEADER in html
        assert ERROR_HTML.REQUIRED_FIELD in html
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_status_open_pending_saved_in_session(self, mock_save):
        session_key = 'draft_barrier__status_form_data'
        expected_form_data = {
            "status": "1",
            "sub_status": "OTHER",
            "sub_status_other": "test",
            "status_summary": "Pending summary",
        }

        response = self.client.post(
            self.url,
            data={
                "status": "1",
                "pending_type": "OTHER",
                "pending_type_other": "test",
                "pending_summary": "Pending summary",
            }
        )
        saved_form_data = self.client.session.get(session_key)

        assert HTTPStatus.FOUND == response.status_code
        assert expected_form_data == saved_form_data
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_status_open_in_progress_saved_in_session(self, mock_save):
        session_key = 'draft_barrier__status_form_data'
        expected_form_data = {
            "status": "2",
            "status_summary": "In progress summary",
        }

        response = self.client.post(
            self.url,
            data={
                "status": "2",
                "open_in_progress_summary": "In progress summary",
            }
        )
        saved_form_data = self.client.session.get(session_key)

        assert HTTPStatus.FOUND == response.status_code
        assert expected_form_data == saved_form_data
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_status_partially_resolved__requires_date(self, mock_save):
        session_key = 'draft_barrier__status_form_data'

        response = self.client.post(self.url, data={'status': '3'})
        saved_form_data = self.client.session.get(session_key)
        html = response.content.decode('utf8')
        form = response.context['form']

        assert form.is_valid() is False
        assert "part_resolved_date" in form.errors
        assert ERROR_HTML.SUMMARY_HEADER in html
        assert ERROR_HTML.REQUIRED_FIELD in html
        assert saved_form_data is None
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_status_partially_resolved__saved_in_session(self, mock_save):
        session_key = 'draft_barrier__status_form_data'
        expected_form_data = {
            'status': '3',
            'status_date': '2019-12-01',
            'status_summary': 'Part resolved summary',
        }

        response = self.client.post(
            self.url,
            data={
                'status': '3',
                'part_resolved_date_0': 12,
                'part_resolved_date_1': 2019,
                'part_resolved_summary': 'Part resolved summary',
            }
        )
        saved_form_data = self.client.session.get(session_key)

        assert HTTPStatus.FOUND == response.status_code
        assert expected_form_data == saved_form_data
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_status_fully_resolved__requires_date(self, mock_save):
        session_key = 'draft_barrier__status_form_data'

        response = self.client.post(self.url, data={'status': '4'})
        saved_form_data = self.client.session.get(session_key)
        html = response.content.decode('utf8')
        form = response.context['form']

        assert form.is_valid() is False
        assert "resolved_date" in form.errors
        assert ERROR_HTML.SUMMARY_HEADER in html
        assert ERROR_HTML.REQUIRED_FIELD in html
        assert saved_form_data is None
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_status_resolved__saved_in_session(self, mock_save):
        session_key = 'draft_barrier__status_form_data'
        expected_form_data = {
            'status': '4',
            'status_date': '2019-12-01',
            'status_summary': 'Resolved summary',
        }

        response = self.client.post(
            self.url,
            data={
                'status': '4',
                'resolved_date_0': 12,
                'resolved_date_1': 2019,
                'resolved_summary': 'Resolved summary',
            },
            follow=True,
        )
        saved_form_data = self.client.session.get(session_key)

        assert HTTPStatus.OK == response.status_code
        assert expected_form_data == saved_form_data
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_success_redirects_to_correct_view(self, mock_save):
        redirect_url = reverse('reports:barrier_location')

        response = self.client.post(
            self.url,
            data={
                'status': '4',
                'resolved_date_0': 12,
                'resolved_date_1': 2019,
                'resolved_summary': 'Resolved summary',
            },
            follow=True,
        )

        self.assertRedirects(response, redirect_url)
        assert mock_save.called is False
