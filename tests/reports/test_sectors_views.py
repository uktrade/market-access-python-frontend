from http import HTTPStatus

from django.urls import reverse, resolve
from mock import patch

from core.tests import ReportsTestCase
from reports.models import Report
from reports.views import NewReportBarrierHasSectorsView, NewReportBarrierSectorsView, NewReportBarrierSectorsAddView
from tests.constants import ERROR_HTML


class HasSectorsViewTestCase(ReportsTestCase):

    def setUp(self):
        super().setUp()
        self.draft = self.draft_barrier(30)
        self.url = reverse('reports:barrier_has_sectors_uuid', kwargs={"barrier_id": self.draft["id"]})

    def test_has_sectors_url_resolves_to_correct_view(self):
        match = resolve(f'/reports/{self.draft["id"]}/has-sectors/')
        assert match.func.view_class == NewReportBarrierHasSectorsView

    def test_has_sectors_view_loads_correct_template(self):
        response = self.client.get(self.url)
        assert HTTPStatus.OK == response.status_code
        self.assertTemplateUsed(response, 'reports/new_report_barrier_sectors_main.html')

    def test_has_sectors_view_returns_correct_html(self):
        expected_title = '<title>Market Access - Add - Sectors affected by the barrier</title>'
        expected_radio_container = '<div class="govuk-radios sectors-affected">'
        radio_item = '<div class="govuk-radios__item">'
        expected_radio_count = 2
        expected_save_btn = '<input type="submit" value="Save and continue" class="govuk-button">'
        expected_exit_btn = '<button type="submit" class="govuk-button button--secondary" '\
                            'name="action" value="exit">Save and exit</button>'

        response = self.client.get(self.url)
        html = response.content.decode('utf8')

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert expected_radio_container in html
        options_count = html.count(radio_item)
        assert expected_radio_count == options_count,\
            f'Expected {expected_radio_count} admin areas, got: {options_count}'
        assert expected_save_btn in html
        assert expected_exit_btn in html

    @patch("reports.helpers.ReportFormGroup.save")
    def test_has_admin_areas_cannot_be_empty(self, mock_save):
        field_name = 'sectors_affected'
        session_key = f'draft_barrier_{self.draft["id"]}_sectors_affected_form_data'

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

    @patch("reports.helpers.ReportFormGroup._update_barrier")
    def test_option_yes_redirects_to_correct_view(self, mock_update):
        """
        Clicking on `Save and continue` when option "Yes" is selected
        should take the user to the .../sectors/ page
        -----
        The session gets updated with the data that comes back from the API
        so to mock this properly, the data has to match what we're sending here.
        Sectors_affected is expected to be set to `true` by the API when we post `1`.
        """
        draft_barrier = self.draft_barrier(31)
        mock_update.return_value = Report(draft_barrier)
        redirect_url = reverse('reports:barrier_sectors_uuid', kwargs={"barrier_id": draft_barrier["id"]})

        response = self.client.post(self.url, data={"sectors_affected": "1"})

        self.assertRedirects(response, redirect_url)
        assert mock_update.called is True

    @patch("reports.helpers.ReportFormGroup._update_barrier")
    def test_option_no_redirects_to_correct_view(self, mock_update):
        """
        Clicking on `Save and continue` when option "No" is selected
        should take the user to the .../problem/ page
        -----
        The session gets updated with the data that comes back from the API
        so to mock this properly, the data has to match what we're sending here.
        Sectors_affected is expected to be set to `false` by the API when we post `0`.
        """
        mock_update.return_value = Report(self.draft)
        redirect_url = reverse('reports:barrier_about_uuid', kwargs={"barrier_id": self.draft["id"]})

        response = self.client.post(self.url, data={"sectors_affected": "0"})

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

        response = self.client.post(self.url, data={"action": "exit", "sectors_affected": "0"})

        self.assertRedirects(response, redirect_url)
        assert mock_update.called is True


class SectorsViewTestCase(ReportsTestCase):

    def setUp(self):
        super().setUp()
        self.draft = self.draft_barrier(310)
        self.url = reverse('reports:barrier_sectors_uuid', kwargs={"barrier_id": self.draft["id"]})

    def test_sectors_url_resolves_to_correct_view(self):
        match = resolve(f'/reports/{self.draft["id"]}/sectors/')
        assert match.func.view_class == NewReportBarrierSectorsView

    def test_sectors_view_loads_correct_template(self):
        response = self.client.get(self.url)
        assert HTTPStatus.OK == response.status_code
        self.assertTemplateUsed(response, 'reports/new_report_barrier_sectors_manage.html')

    def test_sectors_view_returns_correct_html(self):
        expected_title = '<title>Market Access - Add - Sectors affected by the barrier</title>'
        expected_header_text = '<h3 class="selection-list__heading">Selected sectors</h3>'
        sector_item = '<li class="selection-list__list__item">'
        expected_save_btn = '<input type="submit" value="Save and continue" class="govuk-button">'
        expected_exit_btn = (
            '<button type="submit" class="govuk-button button--secondary" '
            'name="action" value="exit">Save and exit</button>'
        )
        add_specific_sector_btn = (
            f'<a href="/reports/{self.draft["id"]}/sectors/add/" '
            'class="govuk-button button--secondary selection-list__add-button">'
            'Add specific sectors</a>'
        )
        select_all_btn = (
            '<button type="submit" class="govuk-button button--secondary selection-list__add-button" '
            'name="action" value="select_all">Select all sectors</button>'
        )

        response = self.client.get(self.url)
        html = response.content.decode('utf8')

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert expected_header_text in html
        assert add_specific_sector_btn in html
        assert select_all_btn in html
        options_count = html.count(sector_item)
        assert 0 == options_count, f'Expected 0 sectors, got: {options_count}'
        assert expected_save_btn in html
        assert expected_exit_btn in html

    def test_sectors_view_displays_selected_sectors(self):
        # set up the session so 2 sections were already selected
        session_key = f'draft_barrier_{self.draft["id"]}_sectors'
        sector_item = '<li class="selection-list__list__item">'
        expected_sections_count = 2
        aerospace_uuid = '9538cecc-5f95-e211-a939-e4115bead28a'
        energy_uuid = 'b1959812-6095-e211-a939-e4115bead28a'

        session = self.client.session
        session[session_key] = f"{aerospace_uuid}, {energy_uuid}"
        session.save()

        response = self.client.get(self.url)
        html = response.content.decode('utf8')

        options_count = html.count(sector_item)
        assert expected_sections_count == options_count, \
            f'Expected {expected_sections_count} admin areas, got: {options_count}'

    def test_remove_sector(self):
        remove_url = reverse('reports:barrier_remove_sector_uuid', kwargs={"barrier_id": self.draft["id"]})
        session_key = f'draft_barrier_{self.draft["id"]}_sectors'
        aerospace_uuid = '9538cecc-5f95-e211-a939-e4115bead28a'
        energy_uuid = 'b1959812-6095-e211-a939-e4115bead28a'
        sector_to_remove = energy_uuid

        session = self.client.session
        session[session_key] = f"{aerospace_uuid}, {energy_uuid}"
        session.save()

        response = self.client.post(remove_url, data={"sector": sector_to_remove}, follow=True)
        selected_admin_areas = self.client.session.get(session_key)

        assert HTTPStatus.OK == response.status_code
        assert aerospace_uuid == selected_admin_areas

    def test_select_all_sectors(self):
        """
        Selecting all sectors should flush any previosuly selected sectors.
        """
        add_all_url = reverse('reports:barrier_add_all_sectors_uuid', kwargs={"barrier_id": self.draft["id"]})
        session_key = f'draft_barrier_{self.draft["id"]}_sectors'
        aerospace_uuid = '9538cecc-5f95-e211-a939-e4115bead28a'
        energy_uuid = 'b1959812-6095-e211-a939-e4115bead28a'

        session = self.client.session
        session[session_key] = f"{aerospace_uuid}, {energy_uuid}"
        session.save()

        response = self.client.post(add_all_url, data={"action": "select_all"}, follow=True)
        selected_admin_areas = self.client.session.get(session_key)

        assert HTTPStatus.OK == response.status_code
        assert "all" == selected_admin_areas

    @patch("reports.helpers.ReportFormGroup._update_barrier")
    def test_save_and_continue_redirects_to_correct_view(self, mock_update):
        """
        Clicking on `Save and continue` should take the user to the .../problem/ page
        """
        mock_update.return_value = Report(self.draft)
        redirect_url = reverse('reports:barrier_about_uuid', kwargs={"barrier_id": self.draft["id"]})

        response = self.client.post(self.url, data={})

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

        response = self.client.post(self.url, data={"action": "exit"})

        self.assertRedirects(response, redirect_url)
        assert mock_update.called is True


class AddSectorsViewTestCase(ReportsTestCase):

    def setUp(self):
        super().setUp()
        self.draft = self.draft_barrier(310)
        self.url = reverse('reports:barrier_add_sectors_uuid', kwargs={"barrier_id": self.draft["id"]})
        self.session_key = f'draft_barrier_{self.draft["id"]}_sectors'

    def test_add_sectors_url_resolves_to_correct_view(self):
        match = resolve(f'/reports/{self.draft["id"]}/sectors/add/')
        assert match.func.view_class == NewReportBarrierSectorsAddView

    def test_add_sectors_view_loads_correct_template(self):
        response = self.client.get(self.url)
        assert HTTPStatus.OK == response.status_code
        self.assertTemplateUsed(response, 'reports/new_report_barrier_sectors_add.html')

    def test_add_sectors_view_returns_correct_html(self):
        expected_title = '<title>Market Access - Add - Sectors affected by the barrier</title>'
        expected_dropdown_container = '<select class="govuk-select govuk-!-width-full" id="sectors" name="sectors">'
        dropdown_option = '<option class="sector_option"'
        expected_add_btn = '<input type="submit" value="Add sector" class="govuk-button">'

        response = self.client.get(self.url)
        html = response.content.decode('utf8')

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert expected_dropdown_container in html
        options_count = html.count(dropdown_option)
        assert 1 <= options_count, f'Expected at least one sector option, got: {options_count}'
        assert expected_add_btn in html

    def test_sectors_cannot_be_empty(self):
        field_name = 'sectors'

        response = self.client.post(self.url, data={field_name: ''})
        saved_form_data = self.client.session.get(self.session_key)
        html = response.content.decode('utf8')
        form = response.context['form']

        assert HTTPStatus.OK == response.status_code
        assert form.is_valid() is False
        assert field_name in form.errors
        assert ERROR_HTML.SUMMARY_HEADER in html
        assert ERROR_HTML.REQUIRED_FIELD in html
        assert saved_form_data is None

    @patch("reports.helpers.ReportFormGroup._update_barrier")
    def test_adding_admin_area_saved_in_session(self, mock_update):
        aerospace_uuid = '9538cecc-5f95-e211-a939-e4115bead28a'
        form_data = {"sectors": aerospace_uuid}
        expected_saved_sectors = aerospace_uuid

        response = self.client.post(self.url, data=form_data, follow=True)
        saved_sectors = self.client.session.get(self.session_key)

        assert HTTPStatus.OK == response.status_code
        assert expected_saved_sectors == saved_sectors
        assert mock_update.called is False

    def test_add_sectors_view_displays_selected_sectors(self):
        # set up the session so 2 sections were already selected
        sector_item = '<li class="selection-list__list__item">'
        expected_sections_count = 2
        aerospace_uuid = '9538cecc-5f95-e211-a939-e4115bead28a'
        energy_uuid = 'b1959812-6095-e211-a939-e4115bead28a'

        session = self.client.session
        session[self.session_key] = f"{aerospace_uuid}, {energy_uuid}"
        session.save()

        response = self.client.get(self.url)
        html = response.content.decode('utf8')

        options_count = html.count(sector_item)
        assert expected_sections_count == options_count,\
            f'Expected {expected_sections_count} admin areas, got: {options_count}'

    @patch("reports.helpers.ReportFormGroup._update_barrier")
    def test_adding_sector_redirects_to_correct_view(self, mock_update):
        field_name = 'sectors'
        aerospace_uuid = '9538cecc-5f95-e211-a939-e4115bead28a'
        redirect_url = reverse('reports:barrier_sectors_uuid', kwargs={"barrier_id": self.draft["id"]})

        response = self.client.post(self.url, data={field_name: aerospace_uuid})

        self.assertRedirects(response, redirect_url)
        assert mock_update.called is False
