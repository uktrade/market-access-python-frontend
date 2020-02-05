from http import HTTPStatus

from django.urls import reverse, resolve
from mock import patch

from core.tests import MarketAccessTestCase
from reports.views import (
    NewReportBarrierProblemStatusView,
    NewReportBarrierStatusView,
)
from tests.constants import ERROR_HTML


class ProblemStatusViewTestCase(MarketAccessTestCase):

    def setUp(self):
        super().setUp()
        self.url = reverse('reports:barrier_problem_status')

    def test_start_url_resolves_to_problem_status_view(self):
        match = resolve('/reports/new/start/')
        assert match.func.view_class == NewReportBarrierProblemStatusView

    def test_problem_status_view_returns_correct_html(self):
        expected_title = '<title>Market Access - Add - Barrier status</title>'
        expected_radio_container = '<div class="govuk-radios problem-status">'
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
    def test_problem_status_cannot_be_empty(self, mock_save):
        field_name = 'status'
        session_key = 'draft_barrier__problem_status_form_data'

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
    def test_problem_status_saved_in_session(self, mock_save):
        field_name = 'status'
        session_key = 'draft_barrier__problem_status_form_data'
        expected_form_data = {'status': '1'}

        response = self.client.post(self.url, data={field_name: '1'}, follow=True)
        saved_form_data = self.client.session.get(session_key)

        assert HTTPStatus.OK == response.status_code
        assert expected_form_data == saved_form_data
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_success_redirects_to_correct_view(self, mock_save):
        field_name = 'status'
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
        expected_radio_container = '<div class="govuk-radios is-resolved govuk-radios--conditional" '\
                                   'data-module="radios">'
        radio_item = '<div class="govuk-radios__item">'
        expected_radio_count = 3
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
    def test_status_unresolved__saved_in_session(self, mock_save):
        field_name = 'status'
        session_key = 'draft_barrier__status_form_data'
        expected_form_data = {
            'status': 'UNRESOLVED',
            'resolved_month': None,
            'resolved_year': None,
            'part_resolved_month': None,
            'part_resolved_year': None,
            'is_resolved': False,
            'resolved_date': ''
        }

        response = self.client.post(self.url, data={field_name: 'UNRESOLVED'})
        saved_form_data = self.client.session.get(session_key)

        assert HTTPStatus.FOUND == response.status_code
        assert expected_form_data == saved_form_data
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_status_partially_resolved__requires_date(self, mock_save):
        month_field_name = 'part_resolved_month'
        year_field_name = 'part_resolved_year'
        session_key = 'draft_barrier__status_form_data'

        response = self.client.post(self.url, data={'status': '3'})
        saved_form_data = self.client.session.get(session_key)
        html = response.content.decode('utf8')
        form = response.context['form']

        assert form.is_valid() is False
        assert month_field_name in form.errors
        assert year_field_name in form.errors
        assert ERROR_HTML.SUMMARY_HEADER in html
        assert ERROR_HTML.REQUIRED_FIELD in html
        assert saved_form_data is None
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_status_partially_resolved__saved_in_session(self, mock_save):
        field_name = 'status'
        session_key = 'draft_barrier__status_form_data'
        expected_form_data = {
            'status': '3',
            'resolved_month': None,
            'resolved_year': None,
            'part_resolved_month': 12,
            'part_resolved_year': 2019,
            'is_resolved': True,
            'resolved_date': '2019-12-01'
        }

        response = self.client.post(
            self.url,
            data={
                field_name: '3',
                'part_resolved_month': 12,
                'part_resolved_year': 2019,
            }
        )
        saved_form_data = self.client.session.get(session_key)

        assert HTTPStatus.FOUND == response.status_code
        assert expected_form_data == saved_form_data
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_status_fully_resolved__requires_date(self, mock_save):
        month_field_name = 'resolved_month'
        year_field_name = 'resolved_year'
        session_key = 'draft_barrier__status_form_data'

        response = self.client.post(self.url, data={'status': '4'})
        saved_form_data = self.client.session.get(session_key)
        html = response.content.decode('utf8')
        form = response.context['form']

        assert form.is_valid() is False
        assert month_field_name in form.errors
        assert year_field_name in form.errors
        assert ERROR_HTML.SUMMARY_HEADER in html
        assert ERROR_HTML.REQUIRED_FIELD in html
        assert saved_form_data is None
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_status_resolved__saved_in_session(self, mock_save):
        field_name = 'status'
        session_key = 'draft_barrier__status_form_data'
        expected_form_data = {
            'status': '4',
            'resolved_month': 12,
            'resolved_year': 2019,
            'part_resolved_month': None,
            'part_resolved_year': None,
            'is_resolved': True,
            'resolved_date': '2019-12-01',
        }

        response = self.client.post(
            self.url,
            data={
                field_name: '4',
                'resolved_month': 12,
                'resolved_year': 2019,
            },
            follow=True,
        )
        saved_form_data = self.client.session.get(session_key)

        assert HTTPStatus.OK == response.status_code
        assert expected_form_data == saved_form_data
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_success_redirects_to_correct_view(self, mock_save):
        field_name = 'status'
        redirect_url = reverse('reports:barrier_location')

        response = self.client.post(
            self.url,
            data={
                field_name: '4',
                'resolved_month': 12,
                'resolved_year': 2019,
            },
            follow=True,
        )

        self.assertRedirects(response, redirect_url)
        assert mock_save.called is False
