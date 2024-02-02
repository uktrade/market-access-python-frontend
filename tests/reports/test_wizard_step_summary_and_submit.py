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
    BarrierPublicEligibilityForm,
    BarrierPublicInformationGateForm,
    BarrierPublicSummaryForm,
    BarrierPublicTitleForm,
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

    def setUp(self):
        # Create mock session data - use named tuple method to create object, not dict
        self.session_mock = namedtuple("session_mock", "prefix data extra_data")
        self.session_data = self.session_mock(
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
                    "barrier-public-eligibility": {},
                    "barrier-public-information-gate": {},
                    "barrier-public-title": {},
                    "barrier-public-summary": {},
                },
                "meta": {"barrier_id": "b9bc718d-f535-413a-a2c0-8868351b44f2"},
            },
        )

        # Create mock steps data - use named tuple method to create object, not dict
        self.steps_mock = namedtuple("steps_mock", "steps current")
        self.steps_data = self.steps_mock(
            steps={
                "barrier-about",
                "barrier-status",
                "barrier-location",
                "barrier-trade-direction",
                "barrier-sectors-affected",
                "barrier-companies-affected",
                "barrier-export-type",
                "barrier-public-eligibility",
                "barrier-public-information-gate",
                "barrier-public-title",
                "barrier-public-summary",
                "barrier-details-summary",
            },
            current="barrier-details-summary",
        )

        # Create mock commodity response object
        self.commodity_mock_object = BarrierCommodity(
            {
                "commodity": "A Thing",
                "code": "1002000000",
                "description": "A Thing",
            }
        )

        self.about_cleaned_data = {"title": "vvvcvcvvbc", "summary": "cbcbcvbcbvc"}
        self.status_cleaned_data = {
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
        self.location_cleaned_data = {
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
        self.trade_direction_cleaned_data = {"trade_direction": "1"}
        self.sector_cleaned_data = {
            "main_sector": "af959812-6095-e211-a939-e4115bead28a",
            "sectors": [
                "9738cecc-5f95-e211-a939-e4115bead28a",
                "9838cecc-5f95-e211-a939-e4115bead28a",
            ],
            "sectors_affected": True,
        }
        self.companies_cleaned_data = {
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
        self.export_types_cleaned_data = {
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
        self.public_eligibility_cleaned_data = {
            "public_eligibility": True,
            "public_eligibility_summary": "",
        }
        self.public_information_gate_cleaned_data = {
            "public_information": True,
        }
        self.public_title_cleaned_data = {
            "title": "The public title",
        }
        self.public_summary_cleaned_data = {
            "summary": "The public summary",
        }

    @patch("utils.api.resources.ReportsResource.get")
    @patch(
        "reports.report_barrier_view.ReportBarrierWizardView.get_cleaned_data_for_step"
    )
    @patch("utils.api.resources.CommoditiesResource.list")
    def test_load_summary_page_full_report(
        self, commodity_api_call_patch, report_get_cleaned_data_patch, report_get_patch
    ):

        # Mock the return of get_cleaned_data method but return different
        # dictionary depending on the passed step name.
        report_get_cleaned_data_patch.side_effect = lambda *step_cleaned_data: {
            ("barrier-about",): self.about_cleaned_data,
            ("barrier-status",): self.status_cleaned_data,
            ("barrier-location",): self.location_cleaned_data,
            ("barrier-trade-direction",): self.trade_direction_cleaned_data,
            ("barrier-sectors-affected",): self.sector_cleaned_data,
            ("barrier-companies-affected",): self.companies_cleaned_data,
            ("barrier-export-type",): self.export_types_cleaned_data,
            ("barrier-public-eligibility",): self.public_eligibility_cleaned_data,
            (
                "barrier-public-information-gate",
            ): self.public_information_gate_cleaned_data,
            ("barrier-public-title",): self.public_title_cleaned_data,
            ("barrier-public-summary",): self.public_summary_cleaned_data,
        }[step_cleaned_data]

        # Initialise view for test
        view = ReportBarrierWizardView()
        view.storage = self.session_data
        view.steps = self.steps_data
        view.prefix = ("wizard_report_barrier_wizard_view",)
        view.client = MarketAccessAPIClient()

        # Set mock return values
        commodity_api_call_patch.return_value = [self.commodity_mock_object]
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
        assert result["public_eligibility"] == "Can be published"
        assert result["public_title"] == "The public title"
        assert result["public_summary"] == "The public summary"

    @patch("utils.api.resources.ReportsResource.get")
    @patch(
        "reports.report_barrier_view.ReportBarrierWizardView.get_cleaned_data_for_step"
    )
    @patch("utils.api.resources.CommoditiesResource.list")
    def test_load_summary_page_ineligible_for_public(
        self, commodity_api_call_patch, report_get_cleaned_data_patch, report_get_patch
    ):

        self.public_eligibility_cleaned_data = {
            "public_eligibility": False,
            "public_eligibility_summary": "This barrier is not public",
        }

        self.session_mock = namedtuple("session_mock", "prefix data extra_data")
        self.session_data = self.session_mock(
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
                    "barrier-public-eligibility": {},
                },
                "meta": {"barrier_id": "b9bc718d-f535-413a-a2c0-8868351b44f2"},
            },
        )

        # Mock the return of get_cleaned_data method but return different
        # dictionary depending on the passed step name.
        report_get_cleaned_data_patch.side_effect = lambda *step_cleaned_data: {
            ("barrier-about",): self.about_cleaned_data,
            ("barrier-status",): self.status_cleaned_data,
            ("barrier-location",): self.location_cleaned_data,
            ("barrier-trade-direction",): self.trade_direction_cleaned_data,
            ("barrier-sectors-affected",): self.sector_cleaned_data,
            ("barrier-companies-affected",): self.companies_cleaned_data,
            ("barrier-export-type",): self.export_types_cleaned_data,
            ("barrier-public-eligibility",): self.public_eligibility_cleaned_data,
        }[step_cleaned_data]

        # Initialise view for test
        view = ReportBarrierWizardView()
        view.storage = self.session_data
        view.steps = self.steps_data
        view.prefix = ("wizard_report_barrier_wizard_view",)
        view.client = MarketAccessAPIClient()

        # Set mock return values
        commodity_api_call_patch.return_value = [self.commodity_mock_object]
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
        assert result["public_eligibility"] == "Cannot be published"
        assert "public_title" not in result.keys()
        assert "public_summary" not in result.keys()

    @patch("utils.api.resources.ReportsResource.get")
    @patch(
        "reports.report_barrier_view.ReportBarrierWizardView.get_cleaned_data_for_step"
    )
    @patch("utils.api.resources.CommoditiesResource.list")
    def test_load_summary_page_eligible_for_public_later(
        self, commodity_api_call_patch, report_get_cleaned_data_patch, report_get_patch
    ):

        self.public_information_gate_cleaned_data = {
            "public_information": False,
        }

        self.session_mock = namedtuple("session_mock", "prefix data extra_data")
        self.session_data = self.session_mock(
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
                    "barrier-public-eligibility": {},
                    "barrier-public-information-gate": {},
                },
                "meta": {"barrier_id": "b9bc718d-f535-413a-a2c0-8868351b44f2"},
            },
        )

        # Mock the return of get_cleaned_data method but return different
        # dictionary depending on the passed step name.
        report_get_cleaned_data_patch.side_effect = lambda *step_cleaned_data: {
            ("barrier-about",): self.about_cleaned_data,
            ("barrier-status",): self.status_cleaned_data,
            ("barrier-location",): self.location_cleaned_data,
            ("barrier-trade-direction",): self.trade_direction_cleaned_data,
            ("barrier-sectors-affected",): self.sector_cleaned_data,
            ("barrier-companies-affected",): self.companies_cleaned_data,
            ("barrier-export-type",): self.export_types_cleaned_data,
            ("barrier-public-eligibility",): self.public_eligibility_cleaned_data,
            (
                "barrier-public-information-gate",
            ): self.public_information_gate_cleaned_data,
        }[step_cleaned_data]

        # Initialise view for test
        view = ReportBarrierWizardView()
        view.storage = self.session_data
        view.steps = self.steps_data
        view.prefix = ("wizard_report_barrier_wizard_view",)
        view.client = MarketAccessAPIClient()

        # Set mock return values
        commodity_api_call_patch.return_value = [self.commodity_mock_object]
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
        assert result["public_eligibility"] == "Can be published"
        assert "public_title" not in result.keys()
        assert "public_summary" not in result.keys()


class SubmitReportTestCase(MarketAccessTestCase):
    # Test suite for starting new barriers
    # make django-test path=reports/test_wizard_step_summary_and_submit.py::SubmitReportTestCase

    def setUp(self):
        # Initialise forms
        self.about_form = BarrierAboutForm()
        self.status_form = BarrierStatusForm()
        self.location_form = BarrierLocationForm()
        self.trade_direction_form = BarrierTradeDirectionForm()
        self.sectors_form = BarrierSectorsAffectedForm()
        self.companies_form = BarrierCompaniesAffectedForm()
        self.export_type_form = BarrierExportTypeForm()
        self.public_eligibility_form = BarrierPublicEligibilityForm()
        self.public_information_gate_form = BarrierPublicInformationGateForm()
        self.public_title_form = BarrierPublicTitleForm()
        self.public_summary_form = BarrierPublicSummaryForm()
        self.summary_form = BarrierDetailsSummaryForm()

        # Set form prefixes for done to identify form correctly
        self.about_form.prefix = "barrier-about"
        self.status_form.prefix = "barrier-status"
        self.location_form.prefix = "barrier-location"
        self.trade_direction_form.prefix = "barrier-trade-direction"
        self.sectors_form.prefix = "barrier-sectors-affected"
        self.companies_form.prefix = "barrier-companies-affected"
        self.export_type_form.prefix = "barrier-export-type"
        self.public_eligibility_form.prefix = "barrier-public-eligibility"
        self.public_information_gate_form.prefix = "barrier-public-information-gate"
        self.public_title_form.prefix = "barrier-public-title"
        self.public_summary_form.prefix = "barrier-public-summary"
        self.summary_form.prefix = "barrier-details-summary"

        # Set expected cleaned data
        self.about_form.cleaned_data = {
            "title": "Fake barrier name",
            "summary": "Fake barrier summary",
        }
        self.status_form.cleaned_data = {
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
        self.location_form.cleaned_data = {
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
        self.trade_direction_form.cleaned_data = {"trade_direction": "1"}
        self.sectors_form.cleaned_data = {
            "main_sector": "9638cecc-5f95-e211-a939-e4115bead28a",
            "sectors": [],
            "sectors_affected": True,
        }
        self.companies_form.cleaned_data = {
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
        self.export_type_form.cleaned_data = {
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
        self.public_eligibility_form.cleaned_data = {
            "public_eligibility": True,
            "public_eligibility_summary": "",
        }
        self.public_information_gate_form.cleaned_data = {
            "public_information": True,
        }
        self.public_title_form.cleaned_data = {
            "title": "The public title",
        }
        self.public_summary_form.cleaned_data = {
            "summary": "The public summary",
        }
        self.summary_form.cleaned_data = {"details_confirmation": "completed"}

        # Build form list for done method arg
        self.form_list = [
            self.about_form,
            self.status_form,
            self.location_form,
            self.trade_direction_form,
            self.sectors_form,
            self.companies_form,
            self.export_type_form,
            self.public_eligibility_form,
            self.public_information_gate_form,
            self.public_title_form,
            self.public_summary_form,
            self.summary_form,
        ]

        # Build form dictionary for done method arg
        self.form_dict = [
            ("barrier-about", self.about_form),
            ("barrier-status", self.status_form),
            ("barrier-location", self.location_form),
            ("barrier-trade-direction", self.trade_direction_form),
            ("barrier-sectors-affected", self.sectors_form),
            ("barrier-companies-affected", self.companies_form),
            ("barrier-export-type", self.export_type_form),
            ("barrier-public-eligibility", self.public_eligibility_form),
            ("barrier-public-information-gate", self.public_information_gate_form),
            ("barrier-public-title", self.public_title_form),
            ("barrier-public-summary", self.public_summary_form),
            ("barrier-details-summary", self.summary_form),
        ]

    @patch("utils.api.resources.ReportsResource.get")
    @patch("utils.api.client.MarketAccessAPIClient.patch")
    @patch("utils.api.resources.ReportsResource.submit")
    @patch("utils.api.resources.PublicBarriersResource.report_public_barrier_field")
    def test_submit_full_report(
        self,
        public_barrier_patch,
        report_submit_patch,
        report_update_patch,
        report_get_patch,
    ):
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

        result = view.done(self.form_list, self.form_dict)

        # Assert page redirected to the barrier information page
        assert result.status_code == 302
        assert result.url == f"/barriers/{self.draft_barrier['id']}/complete/"

        # Assert the report patch mock was called for each form page
        assert report_update_patch.call_count == 8

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
        assert (
            "'public_eligibility': True, " "'public_eligibility_summary': ''"
        ) in str(patch_call_list[7])

        # Assert the report submit mock was called a single time
        report_submit_patch.assert_called_once()

        public_patch_call_list = public_barrier_patch.call_args_list
        assert "'title': 'The public title'" in str(public_patch_call_list[0])
        assert "'summary': 'The public summary'" in str(public_patch_call_list[1])

        # Assert the public barrier was marked as in-progress a single time
        public_barrier_patch.call_count == 2

    @patch("utils.api.resources.ReportsResource.get")
    @patch("utils.api.client.MarketAccessAPIClient.patch")
    @patch("utils.api.resources.ReportsResource.submit")
    @patch("utils.api.resources.PublicBarriersResource.mark_as_in_progress")
    def test_submit_report_ineligible_for_public(
        self,
        public_barrier_patch,
        report_submit_patch,
        report_update_patch,
        report_get_patch,
    ):
        # Remove existing forms from lists/dicts
        self.form_list.pop(10)  # public_summary_form
        self.form_list.pop(9)  # public_title_form
        self.form_list.pop(8)  # public_information_gate_form

        # Override setup cleaned_data & forms
        self.public_eligibility_form.cleaned_data = {
            "public_eligibility": False,
            "public_eligibility_summary": "This barrier is not public",
        }

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

        result = view.done(self.form_list, self.form_dict)

        # Assert page redirected to the barrier information page
        assert result.status_code == 302
        assert result.url == f"/barriers/{self.draft_barrier['id']}/complete/"

        # Assert the report patch mock was called for each form page
        assert report_update_patch.call_count == 8

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
        assert (
            "'public_eligibility': False, "
            "'public_eligibility_summary': 'This barrier is not public'"
        ) in str(patch_call_list[7])

        # Assert the report submit mock was called a single time
        report_submit_patch.assert_called_once()

        # Assert the public barrier was marked as in-progress a single time
        public_barrier_patch.call_count == 0

    @patch("utils.api.resources.ReportsResource.get")
    @patch("utils.api.client.MarketAccessAPIClient.patch")
    @patch("utils.api.resources.ReportsResource.submit")
    @patch("utils.api.resources.PublicBarriersResource.mark_as_in_progress")
    def test_submit_report_eligible_for_public_later(
        self,
        public_barrier_patch,
        report_submit_patch,
        report_update_patch,
        report_get_patch,
    ):
        # Remove existing forms from lists/dicts
        self.form_list.pop(10)  # public_summary_form
        self.form_list.pop(9)  # public_title_form

        # Override setup cleaned_data & forms
        self.public_information_gate_form.cleaned_data = {
            "public_information": False,
        }

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

        result = view.done(self.form_list, self.form_dict)

        # Assert page redirected to the barrier information page
        assert result.status_code == 302
        assert result.url == f"/barriers/{self.draft_barrier['id']}/complete/"

        # Assert the report patch mock was called for each form page
        assert report_update_patch.call_count == 8

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
        assert (
            "'public_eligibility': True, " "'public_eligibility_summary': ''"
        ) in str(patch_call_list[7])

        # Assert the report submit mock was called a single time
        report_submit_patch.assert_called_once()

        # Assert the public barrier was marked as in-progress a single time
        public_barrier_patch.call_count == 0
