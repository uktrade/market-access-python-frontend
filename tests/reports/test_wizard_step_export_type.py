import logging
from collections import namedtuple

from mock import patch

from barriers.models.commodities import BarrierCommodity
from core.tests import MarketAccessTestCase
from reports.report_barrier_forms import BarrierExportTypeForm
from reports.report_barrier_view import ReportBarrierWizardView
from utils.api.client import MarketAccessAPIClient
from utils.api.resources import ReportsResource

logger = logging.getLogger(__name__)


class ReportWizardExportTypeStepTestCase(MarketAccessTestCase):
    # make django-test path=reports/test_wizard_step_export_type.py::ReportWizardExportTypeStepTestCase

    def setUp(self):
        # Dummy data which can be overridden by individual tests
        self.export_types = ["goods", "services", "investments"]
        self.export_description = "the description of the export"
        self.code = ""
        self.location = ""
        self.codes = ["12345", "67890"]
        self.countries = ["80756b9a-5d95-e211-a939-e4115bead28a"]
        self.trading_blocs = [""]

    def test_valid_form_entry_without_hs_codes(self):
        self.codes = None
        form = BarrierExportTypeForm(
            {
                "export_types": self.export_types,
                "export_description": self.export_description,
                "code": self.code,
                "location": self.location,
                "codes": self.codes,
                "countries": self.countries,
                "trading_blocs": self.trading_blocs,
            }
        )

        assert form.is_valid()

        assert form.cleaned_data["commodities"] == []
        assert form.cleaned_data["export_types"] == self.export_types
        assert form.cleaned_data["export_description"] == self.export_description

    def test_valid_form_entry_with_hs_codes(self):
        form = BarrierExportTypeForm(
            {
                "export_types": self.export_types,
                "export_description": self.export_description,
                "code": self.code,
                "location": self.location,
                "codes": self.codes,
                "countries": self.countries,
                "trading_blocs": self.trading_blocs,
            }
        )

        assert form.is_valid()

        first_expected_commodity = {
            "code": "12345",
            "country": "80756b9a-5d95-e211-a939-e4115bead28a",
            "trading_bloc": "",
        }

        second_expected_commodity = {
            "code": "67890",
            "country": "80756b9a-5d95-e211-a939-e4115bead28a",
            "trading_bloc": "",
        }

        assert form.cleaned_data["commodities"] == [
            first_expected_commodity,
            second_expected_commodity,
        ]
        assert form.cleaned_data["export_types"] == self.export_types
        assert form.cleaned_data["export_description"] == self.export_description

    def test_valid_form_entry_with_trading_bloc_hs_codes(self):
        self.trading_blocs = ["TB00016"]
        self.countries = []
        form = BarrierExportTypeForm(
            {
                "export_types": self.export_types,
                "export_description": self.export_description,
                "code": self.code,
                "location": self.location,
                "codes": self.codes,
                "countries": self.countries,
                "trading_blocs": self.trading_blocs,
            }
        )

        assert form.is_valid()

        first_expected_commodity = {
            "code": "12345",
            "country": None,
            "trading_bloc": "TB00016",
        }

        second_expected_commodity = {
            "code": "67890",
            "country": None,
            "trading_bloc": "TB00016",
        }

        assert form.cleaned_data["commodities"] == [
            first_expected_commodity,
            second_expected_commodity,
        ]
        assert form.cleaned_data["export_types"] == self.export_types
        assert form.cleaned_data["export_description"] == self.export_description

    def test_valid_form_entry_with_mixed_source_hs_codes(self):
        self.countries = [
            "a55f66a0-5d95-e211-a939-e4115bead28a",
            "80756b9a-5d95-e211-a939-e4115bead28a",
        ]
        self.trading_blocs = [
            "",
            "",
        ]
        form = BarrierExportTypeForm(
            {
                "export_types": self.export_types,
                "export_description": self.export_description,
                "code": self.code,
                "location": self.location,
                "codes": self.codes,
                "countries": self.countries,
                "trading_blocs": self.trading_blocs,
            }
        )

        assert form.is_valid()

        first_expected_commodity = {
            "code": "12345",
            "country": "a55f66a0-5d95-e211-a939-e4115bead28a",
            "trading_bloc": "",
        }

        second_expected_commodity = {
            "code": "67890",
            "country": "80756b9a-5d95-e211-a939-e4115bead28a",
            "trading_bloc": "",
        }

        assert form.cleaned_data["commodities"] == [
            first_expected_commodity,
            second_expected_commodity,
        ]
        assert form.cleaned_data["export_types"] == self.export_types
        assert form.cleaned_data["export_description"] == self.export_description

    def test_error_missing_export_type(self):
        self.export_types = None
        self.codes = None
        form = BarrierExportTypeForm(
            {
                "export_types": self.export_types,
                "export_description": self.export_description,
                "code": self.code,
                "location": self.location,
                "codes": self.codes,
                "countries": self.countries,
                "trading_blocs": self.trading_blocs,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Select the types of exports the barrier affects."
        assert expected_error_message in form.errors["export_types"]

    def test_error_missing_export_description(self):
        self.export_description = None
        self.codes = None
        form = BarrierExportTypeForm(
            {
                "export_types": self.export_types,
                "export_description": self.export_description,
                "code": self.code,
                "location": self.location,
                "codes": self.codes,
                "countries": self.countries,
                "trading_blocs": self.trading_blocs,
            }
        )

        assert form.is_valid() is False
        expected_error_message = (
            "Enter all goods, services or investments the barrier affects."
        )
        assert expected_error_message in form.errors["export_description"]


class ExportTypePageLoadTestCase(MarketAccessTestCase):
    # Test suite for loading the summary step of the form
    # make django-test path=reports/test_wizard_step_export_type.py::ExportTypePageLoadTestCase

    @patch("utils.api.resources.ReportsResource.get")
    @patch(
        "reports.report_barrier_view.ReportBarrierWizardView.get_cleaned_data_for_step"
    )
    @patch("utils.api.resources.CommoditiesResource.list")
    def test_load_export_types_page_with_entered_data(
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
            current="barrier-export-type",
        )

        # Create mock commodity response object
        commodity_mock_object = BarrierCommodity(
            {
                "commodity": "A Thing",
                "code": "1002000000",
                "description": "Its A Thing",
            }
        )

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
        export_form = BarrierExportTypeForm

        result = view.get_context_data(export_form)

        # Assert the commodity code passed ends with a dictionary representation
        # of the mock result being passed to context
        assert result["confirmed_commodities_data"][0]["commodity"] == {
            "commodity": "A Thing",
            "code": "1002000000",
            "description": "Its A Thing",
        }
