import logging

from core.tests import MarketAccessTestCase
from reports.report_barrier_forms import BarrierExportTypeForm

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
