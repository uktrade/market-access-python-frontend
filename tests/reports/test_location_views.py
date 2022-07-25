from http import HTTPStatus

from django.urls import resolve, reverse
from mock import patch

from core.tests import ReportsTestCase
from reports.models import Report
from reports.views import (
    NewReportBarrierAdminAreasView,
    NewReportBarrierLocationAddAdminAreasView,
    NewReportBarrierLocationHasAdminAreasView,
    NewReportBarrierLocationView,
    NewReportBarrierTradeDirectionView,
)
from tests.constants import ERROR_HTML


class LocationViewTestCase(ReportsTestCase):
    """Country without admin areas."""

    def setUp(self):
        super().setUp()
        self.url = reverse("reports:barrier_location")

    def test_country_url_resolves_to_location_view(self):
        match = resolve("/reports/new/country/")
        assert match.func.view_class == NewReportBarrierLocationView

    def test_location_view_returns_correct_html(self):
        expected_title = "<title>Market Access - Add - Location of the barrier</title>"
        expected_dropdown_container = (
            '<select class="govuk-select" id="location" name="location">'
        )
        dropdown_option = '<option class="location_option"'
        country_count = 195
        expected_continue_btn = (
            '<input type="submit" value="Continue" class="govuk-button">'
        )

        response = self.client.get(self.url)
        html = response.content.decode("utf8")

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert expected_dropdown_container in html
        options_count = html.count(dropdown_option)
        assert (
            country_count < options_count
        ), f"Expected {country_count} or more country options, got: {options_count}"
        assert (
            country_count + 50 > options_count
        ), f"Expected ~{country_count} country options, got: {options_count} - ensure there are no duplicates."
        assert expected_continue_btn in html

    @patch("reports.helpers.ReportFormGroup.save")
    def test_location_cannot_be_empty(self, mock_save):
        field_name = "location"
        session_key = "draft_barrier__location_form_data"

        response = self.client.post(self.url, data={field_name: ""})
        saved_form_data = self.client.session.get(session_key)
        html = response.content.decode("utf8")
        form = response.context["form"]

        assert HTTPStatus.OK == response.status_code
        assert form.is_valid() is False
        assert field_name in form.errors
        assert ERROR_HTML.SUMMARY_HEADER in html
        assert ERROR_HTML.REQUIRED_FIELD in html
        assert saved_form_data is None
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup._create_barrier")
    def test_location_saved_in_session(self, mock_create):
        draft_barrier = self.draft_barrier(2)
        mock_create.return_value = Report(draft_barrier)
        field_name = "location"
        session_key = "draft_barrier__location_form_data"
        fiji_uuid = "d9f682ac-5d95-e211-a939-e4115bead28a"
        expected_form_data = {"country": fiji_uuid, "trading_bloc": ""}

        response = self.client.post(self.url, data={field_name: fiji_uuid}, follow=True)
        saved_form_data = self.client.session.get(session_key)

        assert HTTPStatus.OK == response.status_code
        assert expected_form_data == saved_form_data
        assert mock_create.called is False

    @patch("reports.helpers.ReportFormGroup._create_barrier")
    def test_trading_bloc_location_saved_in_session(self, mock_create):
        draft_barrier = self.draft_barrier(2)
        mock_create.return_value = Report(draft_barrier)
        session_key = "draft_barrier__location_form_data"
        expected_form_data = {"country": None, "trading_bloc": "TB00016"}

        response = self.client.post(self.url, data={"location": "TB00016"}, follow=True)
        saved_form_data = self.client.session.get(session_key)

        assert HTTPStatus.OK == response.status_code
        assert expected_form_data == saved_form_data
        assert mock_create.called is False

    @patch("reports.helpers.ReportFormGroup._create_barrier")
    def test_saving_location_redirects_to_correct_view(self, mock_create):
        draft_barrier = self.draft_barrier(2)
        mock_create.return_value = Report(draft_barrier)
        field_name = "location"
        fiji_uuid = "d9f682ac-5d95-e211-a939-e4115bead28a"
        redirect_url = reverse("reports:barrier_trade_direction")

        response = self.client.post(self.url, data={field_name: fiji_uuid})

        self.assertRedirects(response, redirect_url)
        assert mock_create.called is False

    @patch("reports.helpers.ReportFormGroup._create_barrier")
    def test_saving_location_with_trading_bloc_redirects_to_correct_view(
        self, mock_create
    ):
        draft_barrier = self.draft_barrier(2)
        mock_create.return_value = Report(draft_barrier)
        field_name = "location"
        france_uuid = "82756b9a-5d95-e211-a939-e4115bead28a"
        redirect_url = reverse("reports:barrier_caused_by_trading_bloc")

        response = self.client.post(self.url, data={field_name: france_uuid})

        self.assertRedirects(response, redirect_url)
        assert mock_create.called is False


class LocationViewCausedByTradingBlocTestCase(ReportsTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("reports:barrier_caused_by_trading_bloc")
        session = self.client.session
        france_uuid = "82756b9a-5d95-e211-a939-e4115bead28a"
        session["draft_barrier__location_form_data"] = {"country": france_uuid}
        session.save()

    def test_caused_by_trading_bloc_gets_saved_in_session(self):
        session_key = "draft_barrier__caused_by_trading_bloc_form_data"
        expected_form_data = {"caused_by_trading_bloc": True}

        response = self.client.post(
            self.url,
            data={"caused_by_trading_bloc": "yes"},
            follow=True,
        )
        saved_form_data = self.client.session.get(session_key)
        sess = self.client.session

        assert HTTPStatus.OK == response.status_code
        assert expected_form_data == saved_form_data


class LocationViewHasAdminAreasTestCase(ReportsTestCase):
    """Country with admin areas."""

    @patch("reports.helpers.ReportFormGroup.save")
    def test_saving_location_redirects_to_correct_view(self, mock_save):
        url = reverse("reports:barrier_location")
        field_name = "location"
        us_uuid = "81756b9a-5d95-e211-a939-e4115bead28a"
        redirect_url = reverse("reports:barrier_has_admin_areas")

        response = self.client.post(url, data={field_name: us_uuid})

        self.assertRedirects(response, redirect_url)
        assert mock_save.called is False

    def test_country_url_resolves_to_location_view(self):
        match = resolve("/reports/new/country/has-admin-areas/")
        assert match.func.view_class == NewReportBarrierLocationHasAdminAreasView

    def test_has_admin_areas_view_returns_correct_html(self):
        url = reverse("reports:barrier_has_admin_areas")
        expected_title = "<title>Market Access - Add - Location of the barrier</title>"
        expected_radio_container = '<div class="govuk-radios has-admin-areas">'
        radio_item = '<div class="govuk-radios__item">'
        expected_radio_count = 2
        expected_continue_btn = (
            '<input type="submit" value="Continue" class="govuk-button">'
        )

        response = self.client.get(url)
        html = response.content.decode("utf8")

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert expected_radio_container in html
        radio_count = html.count(radio_item)
        assert (
            expected_radio_count is radio_count
        ), f"Expected {expected_radio_count} radio items, got: {radio_count}"
        assert expected_continue_btn in html

    @patch("reports.helpers.ReportFormGroup.save")
    def test_has_admin_areas_cannot_be_empty(self, mock_save):
        url = reverse("reports:barrier_has_admin_areas")
        field_name = "has_admin_areas"
        session_key = "draft_barrier__has_admin_areas_form_data"

        response = self.client.post(url, data={field_name: ""})
        saved_form_data = self.client.session.get(session_key)
        html = response.content.decode("utf8")
        form = response.context["form"]

        assert HTTPStatus.OK == response.status_code
        assert form.is_valid() is False
        assert field_name in form.errors
        assert ERROR_HTML.SUMMARY_HEADER in html
        assert ERROR_HTML.REQUIRED_FIELD in html
        assert saved_form_data is None
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup._create_barrier")
    def test_has_admin_areas__option_yes_saved_in_session(self, mock_create):
        """
        Question:   Does this affect the entire country?
        Answer:     Yes.
        Behaviour:  No need to add admin areas, the draft barrier does not get saved.
        """
        url = reverse("reports:barrier_has_admin_areas")
        draft_barrier = self.draft_barrier(2)
        mock_create.return_value = Report(draft_barrier)
        field_name = "has_admin_areas"
        session_key = "draft_barrier__has_admin_areas_form_data"
        expected_form_data = {"has_admin_areas": "1"}

        response = self.client.post(url, data={field_name: "1"}, follow=True)
        saved_form_data = self.client.session.get(session_key)

        assert HTTPStatus.OK == response.status_code
        assert expected_form_data == saved_form_data
        assert mock_create.called is False

    @patch("reports.helpers.ReportFormGroup._create_barrier")
    def test_has_admin_areas__option_yes_redirects_to_correct_view(self, mock_create):
        """
        Question:   Does this affect the entire country?
        Answer:     Yes.
        Behaviour:  The form is valid, the user gets redirected to the next step (trade direction).
        """
        url = reverse("reports:barrier_has_admin_areas")
        draft_barrier = self.draft_barrier(2)
        mock_create.return_value = Report(draft_barrier)
        field_name = "has_admin_areas"
        redirect_url = reverse("reports:barrier_trade_direction")

        response = self.client.post(url, data={field_name: "1"})

        self.assertRedirects(response, redirect_url)
        assert mock_create.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_has_admin_areas__option_no_saved_in_session(self, mock_save):
        """
        Question:   Does this affect the entire country?
        Answer:     No.
        Behaviour:  User needs to add admin areas, the barrier is not saved.
        """
        url = reverse("reports:barrier_has_admin_areas")
        field_name = "has_admin_areas"
        session_key = "draft_barrier__has_admin_areas_form_data"
        expected_form_data = {"has_admin_areas": "2"}

        response = self.client.post(url, data={field_name: "2"}, follow=True)
        saved_form_data = self.client.session.get(session_key)

        assert HTTPStatus.OK == response.status_code
        assert expected_form_data == saved_form_data
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup.save")
    def test_has_admin_areas__option_no_redirects_to_correct_view(self, mock_save):
        """
        Question:   Does this affect the entire country?
        Answer:     No.
        Behaviour:  User needs to add admin areas.
                    User gets redirected to add admin area view, draft barrier is not created.
        """
        url = reverse("reports:barrier_has_admin_areas")
        field_name = "has_admin_areas"
        redirect_url = reverse("reports:barrier_add_admin_areas")

        response = self.client.post(url, data={field_name: "2"})

        self.assertRedirects(response, redirect_url)
        assert mock_save.called is False


class LocationViewAddAdminAreasTestCase(ReportsTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("reports:barrier_add_admin_areas")
        brazil_uuid = "b05f66a0-5d95-e211-a939-e4115bead28a"
        session = self.client.session
        session["draft_barrier__location_form_data"] = {"country": brazil_uuid}
        session.save()

    def test_add_admin_areas_url_resolves_to_correct_view(self):
        match = resolve("/reports/new/country/admin-areas/add/")
        assert match.func.view_class == NewReportBarrierLocationAddAdminAreasView

    def test_add_admin_areas_view_returns_correct_html(self):
        expected_title = "<title>Market Access - Add - Location of the barrier</title>"
        expected_dropdown_container = (
            '<select class="govuk-select govuk-!-width-full" id="admin_areas" '
            'name="admin_areas">'
        )
        dropdown_option = '<option class="admin_area_option"'
        expected_add_btn = (
            '<input type="submit" value="Add admin area" class="govuk-button">'
        )

        response = self.client.get(self.url)
        html = response.content.decode("utf8")

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert expected_dropdown_container in html
        options_count = html.count(dropdown_option)
        assert (
            1 <= options_count
        ), f"Expected at least one admin area option, got: {options_count}"
        assert expected_add_btn in html

    def test_admin_area_cannot_be_empty(self):
        field_name = "admin_areas"
        session_key = "draft_barrier__admin_areas_form_data"

        response = self.client.post(self.url, data={field_name: ""})
        saved_form_data = self.client.session.get(session_key)
        html = response.content.decode("utf8")
        form = response.context["form"]

        assert HTTPStatus.OK == response.status_code
        assert form.is_valid() is False
        assert field_name in form.errors
        assert ERROR_HTML.SUMMARY_HEADER in html
        assert ERROR_HTML.REQUIRED_FIELD in html
        assert saved_form_data is None

    @patch("reports.helpers.ReportFormGroup._create_barrier")
    def test_adding_admin_area_saved_in_session(self, mock_create):
        field_name = "admin_areas"
        session_key = "draft_barrier__admin_areas_form_data"
        acre_uuid = "b5d03d97-fef5-4da6-9117-98a4d633b581"
        expected_admin_areas = {"admin_areas": "b5d03d97-fef5-4da6-9117-98a4d633b581"}

        response = self.client.post(self.url, data={field_name: acre_uuid}, follow=True)
        saved_admin_areas = self.client.session.get(session_key)

        assert HTTPStatus.OK == response.status_code
        assert expected_admin_areas == saved_admin_areas
        assert mock_create.called is False

    @patch("reports.helpers.ReportFormGroup._create_barrier")
    def test_adding_admin_area_redirects_to_correct_view(self, mock_create):
        field_name = "admin_areas"
        acre_uuid = "b5d03d97-fef5-4da6-9117-98a4d633b581"
        redirect_url = reverse("reports:barrier_admin_areas")

        response = self.client.post(self.url, data={field_name: acre_uuid})

        self.assertRedirects(response, redirect_url)
        assert mock_create.called is False


class LocationViewAdminAreasTestCase(ReportsTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("reports:barrier_admin_areas")
        brazil_uuid = "b05f66a0-5d95-e211-a939-e4115bead28a"
        session = self.client.session
        session["draft_barrier__location_form_data"] = {"country": brazil_uuid}
        session.save()

    def test_admin_areas_url_resolves_to_correct_view(self):
        match = resolve("/reports/new/country/admin-areas/")
        assert match.func.view_class == NewReportBarrierAdminAreasView

    def test_admin_areas_view_loads_correct_template(self):
        response = self.client.get(self.url)
        assert HTTPStatus.OK == response.status_code
        self.assertTemplateUsed(
            response, "reports/new_report_barrier_location_admin_areas.html"
        )

    def test_admin_areas_view_returns_correct_html(self):
        expected_title = "<title>Market Access - Add - Location of the barrier</title>"
        expected_header_text = (
            '<h3 class="selection-list__heading">Selected admin areas</h3>'
        )
        admin_area_item = '<li class="selection-list__list__item">'
        expected_continue_btn = (
            '<input type="submit" value="Continue" class="govuk-button">'
        )
        add_another_btn = (
            '<a href="/reports/new/country/admin-areas/add/" '
            'class="govuk-button button--secondary '
            'selection-list__add-button">Add another admin area</a>'
        )

        response = self.client.get(self.url)
        html = response.content.decode("utf8")

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert expected_header_text in html
        assert add_another_btn in html
        options_count = html.count(admin_area_item)
        assert 0 == options_count, f"Expected 0 admin areas, got: {options_count}"
        assert expected_continue_btn in html

    def test_admin_areas_view_displays_selected_admin_areas(self):
        # set up the session so 2 admin areas were already added
        admin_area_item = '<li class="selection-list__list__item">'
        expected_admin_areas_count = 2

        session = self.client.session
        acre_uuid = "b5d03d97-fef5-4da6-9117-98a4d633b581"
        bahia_uuid = "5b76e167-a548-4aca-8d49-39c19e646425"
        session["draft_barrier__selected_admin_areas"] = f"{acre_uuid}, {bahia_uuid}"
        session.save()

        response = self.client.get(self.url)
        html = response.content.decode("utf8")

        options_count = html.count(admin_area_item)
        assert (
            expected_admin_areas_count == options_count
        ), f"Expected {expected_admin_areas_count} admin areas, got: {options_count}"

    def test_remove_admin_area(self):
        remove_url = reverse("reports:barrier_remove_admin_areas")
        session_key = "draft_barrier__selected_admin_areas"
        acre_uuid = "b5d03d97-fef5-4da6-9117-98a4d633b581"
        bahia_uuid = "5b76e167-a548-4aca-8d49-39c19e646425"
        area_to_remove = acre_uuid

        session = self.client.session
        session[session_key] = f"{acre_uuid}, {bahia_uuid}"
        session.save()

        response = self.client.post(
            remove_url, data={"admin_area": area_to_remove}, follow=True
        )
        selected_admin_areas = self.client.session.get(session_key)

        assert HTTPStatus.OK == response.status_code
        assert bahia_uuid == selected_admin_areas

    @patch("reports.helpers.ReportFormGroup._create_barrier")
    def test_button_continue_redirects_to_correct_view(self, mock_create):
        """
        Clicking on `Continue` button should proceed to trade directions without saving the barrier
        """
        draft_barrier = self.draft_barrier(2)
        mock_create.return_value = Report(draft_barrier)
        redirect_url = reverse("reports:barrier_trade_direction")

        response = self.client.post(self.url, data={})

        self.assertRedirects(response, redirect_url)
        assert mock_create.called is False


class TradeDirectionViewTestCase(ReportsTestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("reports:barrier_trade_direction")

    def test_trade_direction_url_resolves_to_correct_view(self):
        match = resolve("/reports/new/trade-direction/")
        assert match.func.view_class == NewReportBarrierTradeDirectionView

    def test_trade_direction_view_returns_correct_html(self):
        expected_title = "<title>Market Access - Add - Location of the barrier</title>"
        expected_radio_container = '<div class="govuk-radios trade_direction"'
        radio_item = '<div class="govuk-radios__item">'
        expected_radio_count = 2
        expected_save_btn = (
            '<input type="submit" value="Save and continue" class="govuk-button">'
        )
        expected_exit_btn = (
            '<button type="submit" class="govuk-button button--secondary" '
            'name="action" value="exit">Save and exit</button>'
        )

        response = self.client.get(self.url)
        html = response.content.decode("utf8")

        assert HTTPStatus.OK == response.status_code
        assert expected_title in html
        assert expected_radio_container in html
        radio_count = html.count(radio_item)
        assert (
            expected_radio_count is radio_count
        ), f"Expected {expected_radio_count} radio items, got: {radio_count}"
        assert expected_save_btn in html
        assert expected_exit_btn in html

    @patch("reports.helpers.ReportFormGroup.save")
    def test_trade_direction_cannot_be_empty(self, mock_save):
        field_name = "trade_direction"
        session_key = "draft_barrier__trade_direction_form_data"

        response = self.client.post(self.url, data={field_name: ""})
        saved_form_data = self.client.session.get(session_key)
        html = response.content.decode("utf8")
        form = response.context["form"]

        assert HTTPStatus.OK == response.status_code
        assert form.is_valid() is False
        assert field_name in form.errors
        assert ERROR_HTML.SUMMARY_HEADER in html
        assert ERROR_HTML.REQUIRED_FIELD in html
        assert saved_form_data is None
        assert mock_save.called is False

    @patch("reports.helpers.ReportFormGroup._create_barrier")
    def test_trade_direction_gets_saved_in_session(self, mock_create):
        draft_barrier = self.draft_barrier(2)
        mock_create.return_value = Report(draft_barrier)
        field_name = "trade_direction"
        export = 1
        session_key = f'draft_barrier_{draft_barrier["id"]}_trade_direction_form_data'
        expected_form_data = {"trade_direction": export}

        response = self.client.post(self.url, data={field_name: "1"}, follow=True)
        saved_form_data = self.client.session.get(session_key)

        assert HTTPStatus.OK == response.status_code
        assert expected_form_data == saved_form_data
        assert mock_create.called is True

    @patch("reports.helpers.ReportFormGroup._create_barrier")
    def test_button_save_and_continue_redirects_to_correct_view(self, mock_create):
        """
        Clicking on `Save and continue` button should create a draft barrier
        """
        field_name = "trade_direction"
        export = "1"
        draft_barrier = self.draft_barrier(2)
        mock_create.return_value = Report(draft_barrier)
        redirect_url = reverse(
            "reports:barrier_has_sectors_uuid",
            kwargs={"barrier_id": draft_barrier["id"]},
        )

        response = self.client.post(self.url, data={field_name: export})

        self.assertRedirects(response, redirect_url)
        assert mock_create.called is True

    @patch("utils.api.client.ReportsResource.get")
    @patch("reports.helpers.ReportFormGroup._create_barrier")
    def test_button_save_and_exit_redirects_to_correct_view(
        self, mock_create, mock_get
    ):
        """
        Clicking on `Save and exit` button should create a draft barrier
        and redirect the user to the draft barrier details view
        """
        field_name = "trade_direction"
        export = "1"
        draft_barrier = self.draft_barrier(2)
        mock_create.return_value = Report(draft_barrier)
        mock_get.return_value = Report(draft_barrier)
        redirect_url = reverse(
            "reports:draft_barrier_details_uuid",
            kwargs={"barrier_id": draft_barrier["id"]},
        )

        payload = {field_name: export, "action": "exit"}
        response = self.client.post(self.url, data=payload)

        self.assertRedirects(response, redirect_url)
        assert mock_create.called is True
