import datetime
import logging
from collections import namedtuple

from mock import patch

from barriers.models.commodities import BarrierCommodity
from core.tests import MarketAccessTestCase
from reports.report_barrier_forms import (
    BarrierAboutForm,
    BarrierCompaniesAffectedForm,
    BarrierDetailsSummaryForm,
    BarrierExportTypeForm,
    BarrierLocationForm,
    BarrierSectorsAffectedForm,
    BarrierStatusForm,
    BarrierTradeDirectionForm,
)
from reports.report_barrier_view import ReportBarrierWizardView
from utils.api.client import MarketAccessAPIClient
from utils.api.resources import ReportsResource

logger = logging.getLogger(__name__)


class SummaryPageLoadTestCase(MarketAccessTestCase):
    # Test suite for loading the summary step of the form
    # make django-test path=reports/test_wizard_step_summary_and_submit.py::SummaryPageLoadTestCase

    @patch("utils.api.resources.ReportsResource.get")
    @patch(
        "reports.report_barrier_view.ReportBarrierWizardView.get_cleaned_data_for_step"
    )
    @patch("utils.api.resources.CommoditiesResource.list")
    def test_load_summary_page(
        self, commodity_api_call_patch, report_get_cleaned_data_patch, report_get_patch
    ):
        # Create mock session data - use named tuple method to create object, not dict
        session_mock = namedtuple("session_mock", "prefix data extra_data")
        session_data = session_mock(
            prefix="wizard_report_barrier_wizard_view",
            extra_data={},
            data={
                "step": "barrier-details-summary",
                "step_data": {
                    "barrier-about": {},
                    "barrier-status": {},
                    "barrier-location": {},
                    "barrier-trade-direction": {},
                    "barrier-sectors-affected": {},
                    "barrier-companies-affected": {},
                    "barrier-export-type": {},
                },
                "meta": {"barrier_id": "b9bc718d-f535-413a-a2c0-8868351b44f2"},
            },
        )

        # Create mock steps data - use named tuple method to create object, not dict
        steps_mock = namedtuple("steps_mock", "steps current")
        steps_data = steps_mock(
            steps={
                "barrier-about",
                "barrier-status",
                "barrier-location",
                "barrier-trade-direction",
                "barrier-sectors-affected",
                "barrier-companies-affected",
                "barrier-export-type",
                "barrier-details-summary",
            },
            current="barrier-details-summary",
        )

        # Create mock commodity response object
        commodity_mock_object = BarrierCommodity(
            {
                "commodity": "A Thing",
                "code": "1002000000",
                "description": "A Thing",
            }
        )

        about_cleaned_data = {"title": "vvvcvcvvbc", "summary": "cbcbcvbcbvc"}
        status_cleaned_data = {
            "status": "2",
            "partially_resolved_date": None,
            "partially_resolved_description": "",
            "resolved_date": None,
            "resolved_description": "",
            "start_date_unknown": True,
            "start_date": None,
            "currently_active": "NO",
            "status_date": datetime.date(2023, 7, 31),
            "status_summary": "",
            "start_date_known": False,
            "is_currently_active": "NO",
        }
        location_cleaned_data = {
            "location_select": "TB00016",
            "affect_whole_country": True,
            "admin_areas": [],
            "trading_bloc_EU": "",
            "trading_bloc_GCC": "",
            "trading_bloc_EAEU": "",
            "trading_bloc_Mercosur": "",
            "country": None,
            "trading_bloc": "TB00016",
            "caused_by_trading_bloc": False,
            "caused_by_admin_areas": False,
        }
        trade_direction_cleaned_data = {"trade_direction": "1"}
        sector_cleaned_data = {
            "main_sector": "af959812-6095-e211-a939-e4115bead28a",
            "sectors": [
                "9738cecc-5f95-e211-a939-e4115bead28a",
                "9838cecc-5f95-e211-a939-e4115bead28a",
            ],
            "sectors_affected": True,
        }
        companies_cleaned_data = {
            "companies_affected": (
                "[{"
                '"company_number":"10590916",'
                '"address":{'
                '"premises":"26",'
                '"region":"Essex",'
                '"postal_code":"RM5 2SP",'
                '"address_line_1":"Warden Avenue",'
                "},"
                '"company_type":"ltd",'
                '"description_identifier":["incorporated-on"],'
                '"company_status":"active",'
                '"links":{"self":"/company/10590916"},'
                '"address_snippet":"26 Warden Avenue, Romford, Essex, United Kingdom, RM5 2SP",'
                '"title":"BLAH LTD",'
                '"date_of_creation":"2017-01-30",'
                "}]"
            ),
            "unrecognised_company": '["Fake Company"]',
            "companies": [{"id": "10590916", "name": "BLAH LTD"}],
            "related_organisations": [{"id": "", "name": "Fake Company"}],
        }
        export_types_cleaned_data = {
            "export_types": ["goods"],
            "export_description": "An export description",
            "code": "",
            "location": "",
            "codes": ["1002000000"],
            "countries": ["80756b9a-5d95-e211-a939-e4115bead28a"],
            "trading_blocs": [],
            "commodities": [
                {
                    "code": "1002000000",
                    "country": "80756b9a-5d95-e211-a939-e4115bead28a",
                    "trading_bloc": "",
                }
            ],
        }

        # Mock the return of get_cleaned_data method but return different
        # dictionary depending on the passed step name.
        report_get_cleaned_data_patch.side_effect = lambda *step_cleaned_data: {
            ("barrier-about",): about_cleaned_data,
            ("barrier-status",): status_cleaned_data,
            ("barrier-location",): location_cleaned_data,
            ("barrier-trade-direction",): trade_direction_cleaned_data,
            ("barrier-sectors-affected",): sector_cleaned_data,
            ("barrier-companies-affected",): companies_cleaned_data,
            ("barrier-export-type",): export_types_cleaned_data,
        }[step_cleaned_data]

        # Initialise view for test
        view = ReportBarrierWizardView()
        view.storage = session_data
        view.steps = steps_data
        view.prefix = ("wizard_report_barrier_wizard_view",)
        view.client = MarketAccessAPIClient()

        # Set mock return values
        commodity_api_call_patch.return_value = [commodity_mock_object]
        report_get_patch.return_value = ReportsResource.model(self.draft_barrier)
        summary_form = BarrierDetailsSummaryForm()

        result = view.get_context_data(summary_form)

        # Assert the transformations of stored data to readble values for the summary table
        # have taken place and have been passed to the form in context.
        assert result["status"] == "Open"
        assert result["barrier_location"] == "European Union"
        assert (
            result["trade_direction"] == "Exporting from the UK or investing overseas"
        )
        assert result["main_sector"] == "Advanced Engineering"
        assert result["sectors"] == ["Airports", "Automotive"]
        assert result["companies"] == ["BLAH LTD"]
        assert result["related_organisations"] == ["Fake Company"]
        assert result["codes"] == [{"code": "1002000000", "description": "A Thing"}]


class SubmitReportTestCase(MarketAccessTestCase):
    # Test suite for starting new barriers
    # make django-test path=reports/test_wizard_step_summary_and_submit.py::SubmitReportTestCase

    @patch("utils.api.resources.ReportsResource.get")
    @patch("utils.api.client.MarketAccessAPIClient.patch")
    @patch("utils.api.resources.ReportsResource.submit")
    def test_submit_full_report(
        self, report_submit_patch, report_update_patch, report_get_patch
    ):

        # Initialise forms
        about_form = BarrierAboutForm()
        status_form = BarrierStatusForm()
        location_form = BarrierLocationForm()
        trade_direction_form = BarrierTradeDirectionForm()
        sectors_form = BarrierSectorsAffectedForm()
        companies_form = BarrierCompaniesAffectedForm()
        export_type_form = BarrierExportTypeForm()
        summary_form = BarrierDetailsSummaryForm()

        # Set form prefixes for done to identify form correctly
        about_form.prefix = "barrier-about"
        status_form.prefix = "barrier-status"
        location_form.prefix = "barrier-location"
        trade_direction_form.prefix = "barrier-trade-direction"
        sectors_form.prefix = "barrier-sectors-affected"
        companies_form.prefix = "barrier-companies-affected"
        export_type_form.prefix = "barrier-export-type"
        summary_form.prefix = "barrier-details-summary"

        # Set expected cleaned data
        about_form.cleaned_data = {
            "title": "Fake barrier name",
            "summary": "Fake barrier summary",
        }
        status_form.cleaned_data = {
            "status": "2",
            "partially_resolved_date": None,
            "partially_resolved_description": "",
            "resolved_date": None,
            "resolved_description": "",
            "start_date_unknown": True,
            "start_date": None,
            "currently_active": "YES",
            "status_date": datetime.date(2023, 7, 24),
            "status_summary": "",
            "start_date_known": False,
            "is_currently_active": "YES",
        }
        location_form.cleaned_data = {
            "location_select": "985f66a0-5d95-e211-a939-e4115bead28a",
            "affect_whole_country": True,
            "admin_areas": [],
            "trading_bloc_EU": "",
            "trading_bloc_GCC": "",
            "trading_bloc_EAEU": "",
            "trading_bloc_Mercosur": "",
            "country": "985f66a0-5d95-e211-a939-e4115bead28a",
            "trading_bloc": "",
            "caused_by_trading_bloc": False,
            "caused_by_admin_areas": False,
        }
        trade_direction_form.cleaned_data = {"trade_direction": "1"}
        sectors_form.cleaned_data = {
            "main_sector": "9638cecc-5f95-e211-a939-e4115bead28a",
            "sectors": [],
            "sectors_affected": True,
        }
        companies_form.cleaned_data = {
            "companies_affected": (
                "[{"
                '"company_status":"active",'
                '"company_number":"10590916",'
                '"title":"BLAH LTD",'
                '"company_type":"ltd",'
                '"date_of_creation":"2017-01-30",'
                "}]"
            ),
            "unrecognised_company": "",
            "companies": [{"id": "10590916", "name": "BLAH LTD"}],
            "related_organisations": [],
        }
        export_type_form.cleaned_data = {
            "export_types": ["goods", "services"],
            "export_description": "A description of the export.",
            "code": "",
            "location": "",
            "codes": ["1001000000"],
            "countries": ["80756b9a-5d95-e211-a939-e4115bead28a"],
            "trading_blocs": [],
            "commodities": [
                {
                    "code": "1001000000",
                    "country": "80756b9a-5d95-e211-a939-e4115bead28a",
                    "trading_bloc": "",
                }
            ],
        }
        summary_form.cleaned_data = {"details_confirmation": "completed"}

        # Build form list for done method arg
        form_list = [
            about_form,
            status_form,
            location_form,
            trade_direction_form,
            sectors_form,
            companies_form,
            export_type_form,
            summary_form,
        ]

        # Build form dictionary for done method arg
        form_dict = [
            ("barrier-about", about_form),
            ("barrier-status", status_form),
            ("barrier-location", location_form),
            ("barrier-trade-direction", trade_direction_form),
            ("barrier-sectors-affected", sectors_form),
            ("barrier-companies-affected", companies_form),
            ("barrier-export-type", export_type_form),
            ("barrier-details-summary", summary_form),
        ]

        # Create mock session data
        session_mock = namedtuple("session_mock", "prefix data")
        session_data = session_mock(
            prefix="wizard_report_barrier_wizard_view",
            data={"meta": {"barrier_id": "barrier-id-goes-here"}},
        )

        # Initialise view for test
        view = ReportBarrierWizardView()
        view.storage = session_data
        view.client = MarketAccessAPIClient()

        # Set mock return values
        report_get_patch.return_value = ReportsResource.model(self.draft_barrier)

        result = view.done(form_list, form_dict)

        # Assert page redirected to the barrier information page
        assert result.status_code == 302
        assert result.url == f"/barriers/{self.draft_barrier['id']}/complete/"

        # Assert the report patch mock was called for each form page
        assert report_update_patch.call_count == 7

        # Assert the correct fields from cleaned_data have been included in a patch call
        patch_call_list = report_update_patch.call_args_list
        # About fields
        assert "'title': 'Fake barrier name'" in str(patch_call_list[0])
        assert "'summary': 'Fake barrier summary'" in str(patch_call_list[0])
        # Status fields
        assert "'status': '2'" in str(patch_call_list[1])
        assert "'start_date': None" in str(patch_call_list[1])
        assert "'currently_active': 'YES'" in str(patch_call_list[1])
        assert "'status_date': '2023-07-24'" in str(patch_call_list[1])
        assert "'status_summary': ''" in str(patch_call_list[1])
        assert "'start_date_known': False" in str(patch_call_list[1])
        assert "'is_currently_active': 'YES'" in str(patch_call_list[1])
        # Location fields
        assert "'affect_whole_country': True" in str(patch_call_list[2])
        assert "'admin_areas': []" in str(patch_call_list[2])
        assert "'country': '985f66a0-5d95-e211-a939-e4115bead28a'" in str(
            patch_call_list[2]
        )
        assert "'trading_bloc': ''" in str(patch_call_list[2])
        assert "'caused_by_trading_bloc': False" in str(patch_call_list[2])
        assert "'caused_by_admin_areas': False" in str(patch_call_list[2])
        # Trade direction fields
        assert "'trade_direction': '1'" in str(patch_call_list[3])
        # Sector fields
        assert "'main_sector': '9638cecc-5f95-e211-a939-e4115bead28a'" in str(
            patch_call_list[4]
        )
        assert "'sectors': []" in str(patch_call_list[4])
        assert "'sectors_affected': True" in str(patch_call_list[4])
        # Companies fields
        assert "'companies': [{'id': '10590916', 'name': 'BLAH LTD'}]" in str(
            patch_call_list[5]
        )
        assert "'related_organisations': []" in str(patch_call_list[5])
        # Export types fields
        patch_call_list[6]
        assert "'export_types': ['goods', 'services']" in str(patch_call_list[6])
        assert "'export_description': 'A description of the export.'" in str(
            patch_call_list[6]
        )
        assert (
            "'commodities': [{'code': '1001000000', "
            "'country': '80756b9a-5d95-e211-a939-e4115bead28a', 'trading_bloc': ''}]"
        ) in str(patch_call_list[6])

        # Assert the report submit mock was called a single time
        report_submit_patch.assert_called_once()
