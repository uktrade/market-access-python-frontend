import datetime
import logging
from collections import namedtuple

from mock import patch

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
