import logging

from core.tests import MarketAccessTestCase
from reports.report_barrier_forms import BarrierSectorsAffectedForm

logger = logging.getLogger(__name__)


class ReportWizardSectorsStepTestCase(MarketAccessTestCase):
    # make django-test path=reports/test_wizard_step_sectors.py::ReportWizardSectorsStepTestCase

    def setUp(self):
        # Dummy data which can be overridden by individual tests
        self.main_sector = "af959812-6095-e211-a939-e4115bead28a"
        self.sectors = """[
            "9638cecc-5f95-e211-a939-e4115bead28a",
            "9738cecc-5f95-e211-a939-e4115bead28a"
        ]"""

    def test_valid_form_entry_main_and_other_sectors(self):
        form = BarrierSectorsAffectedForm(
            {
                "main_sector": self.main_sector,
                "sectors": self.sectors,
            }
        )

        assert form.is_valid()
        assert self.main_sector in form.cleaned_data["main_sector"]
        assert form.cleaned_data["sectors"] == [
            "9638cecc-5f95-e211-a939-e4115bead28a",
            "9738cecc-5f95-e211-a939-e4115bead28a",
        ]
        assert form.cleaned_data["sectors_affected"] is True

    def test_valid_form_entry_main_sector_only(self):
        self.sectors = None
        form = BarrierSectorsAffectedForm(
            {
                "main_sector": self.main_sector,
                "sectors": self.sectors,
            }
        )

        assert form.is_valid()
        assert self.main_sector in form.cleaned_data["main_sector"]
        assert form.cleaned_data["sectors"] == []
        assert form.cleaned_data["sectors_affected"] is True

    def test_error_missing_main_sector(self):
        self.main_sector = None
        self.sectors = None
        form = BarrierSectorsAffectedForm(
            {
                "main_sector": self.main_sector,
                "sectors": self.sectors,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Select the sector affected the most"
        assert expected_error_message in form.errors["main_sector"]
