import logging

from core.tests import MarketAccessTestCase
from reports.report_barrier_forms import BarrierLocationForm

logger = logging.getLogger(__name__)


class ReportWizardLocationStepTestCase(MarketAccessTestCase):
    # make django-test path=reports/test_wizard_step_location.py::ReportWizardLocationStepTestCase

    def setUp(self):
        # Dummy data which can be overridden by individual tests
        self.location_select = "b05f66a0-5d95-e211-a939-e4115bead28a"
        self.affect_whole_country = True
        self.admin_areas = None
        self.trading_bloc_EU = None
        self.trading_bloc_GCC = None
        self.trading_bloc_EAEU = None
        self.trading_bloc_Mercosur = None

    def test_valid_form_entry_single_country(self):
        form = BarrierLocationForm(
            {
                "location_select": self.location_select,
                "affect_whole_country": self.affect_whole_country,
                "admin_areas": self.admin_areas,
                "trading_bloc_EU": self.trading_bloc_EU,
                "trading_bloc_GCC": self.trading_bloc_GCC,
                "trading_bloc_EAEU": self.trading_bloc_EAEU,
                "trading_bloc_Mercosur": self.trading_bloc_Mercosur,
                "barrier-location-affect_whole_country": self.affect_whole_country,
            }
        )

        assert form.is_valid()
        assert self.location_select in form.cleaned_data["country"]
        assert form.cleaned_data["caused_by_trading_bloc"] is False

    def test_valid_form_entry_trading_bloc_affected(self):
        self.location_select = "TB00016"
        form = BarrierLocationForm(
            {
                "location_select": self.location_select,
                "affect_whole_country": self.affect_whole_country,
                "admin_areas": self.admin_areas,
                "trading_bloc_EU": self.trading_bloc_EU,
                "trading_bloc_GCC": self.trading_bloc_GCC,
                "trading_bloc_EAEU": self.trading_bloc_EAEU,
                "trading_bloc_Mercosur": self.trading_bloc_Mercosur,
            }
        )

        assert form.is_valid()
        assert self.location_select in form.cleaned_data["trading_bloc"]

    def test_valid_form_entry_caused_by_trading_bloc(self):
        self.trading_bloc_Mercosur = "YES"
        form = BarrierLocationForm(
            {
                "location_select": self.location_select,
                "affect_whole_country": self.affect_whole_country,
                "admin_areas": self.admin_areas,
                "trading_bloc_EU": self.trading_bloc_EU,
                "trading_bloc_GCC": self.trading_bloc_GCC,
                "trading_bloc_EAEU": self.trading_bloc_EAEU,
                "trading_bloc_Mercosur": self.trading_bloc_Mercosur,
                "barrier-location-affect_whole_country": self.affect_whole_country,
            }
        )

        assert form.is_valid()
        assert self.location_select in form.cleaned_data["country"]
        assert form.cleaned_data["caused_by_trading_bloc"] is True

    def test_valid_form_entry_with_admin_areas(self):
        self.trading_bloc_Mercosur = "NO"
        self.affect_whole_country = False
        self.admin_areas = (
            "b5d03d97-fef5-4da6-9117-98a4d633b581,b0dd060f-4627-499a-a298-7289c5abb89b"
        )
        form = BarrierLocationForm(
            {
                "location_select": self.location_select,
                "affect_whole_country": self.affect_whole_country,
                "admin_areas": self.admin_areas,
                "trading_bloc_EU": self.trading_bloc_EU,
                "trading_bloc_GCC": self.trading_bloc_GCC,
                "trading_bloc_EAEU": self.trading_bloc_EAEU,
                "trading_bloc_Mercosur": self.trading_bloc_Mercosur,
                "barrier-location-affect_whole_country": self.affect_whole_country,
            }
        )

        assert form.is_valid()
        assert self.location_select in form.cleaned_data["country"]
        assert form.cleaned_data["caused_by_trading_bloc"] is False
        assert form.cleaned_data["caused_by_admin_areas"] is True
        assert form.cleaned_data["admin_areas"] == [
            "b5d03d97-fef5-4da6-9117-98a4d633b581",
            "b0dd060f-4627-499a-a298-7289c5abb89b",
        ]

    def test_error_admin_areas_missing(self):
        self.trading_bloc_Mercosur = "NO"
        self.affect_whole_country = False
        self.admin_areas = None
        form = BarrierLocationForm(
            {
                "location_select": self.location_select,
                "affect_whole_country": self.affect_whole_country,
                "admin_areas": self.admin_areas,
                "trading_bloc_EU": self.trading_bloc_EU,
                "trading_bloc_GCC": self.trading_bloc_GCC,
                "trading_bloc_EAEU": self.trading_bloc_EAEU,
                "trading_bloc_Mercosur": self.trading_bloc_Mercosur,
                "barrier-location-affect_whole_country": self.affect_whole_country,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Select all admin areas the barrier relates to"
        assert expected_error_message in form.errors["admin_areas"]

    def test_error_country_not_selected(self):
        self.location_select = "0"
        form = BarrierLocationForm(
            {
                "location_select": self.location_select,
                "affect_whole_country": self.affect_whole_country,
                "admin_areas": self.admin_areas,
                "trading_bloc_EU": self.trading_bloc_EU,
                "trading_bloc_GCC": self.trading_bloc_GCC,
                "trading_bloc_EAEU": self.trading_bloc_EAEU,
                "trading_bloc_Mercosur": self.trading_bloc_Mercosur,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Select which location the barrier relates to"
        assert expected_error_message in form.errors["location_select"]

    def test_error_affect_whole_country_not_selected(self):
        # Set location to USA as this has admin areas and triggers "whole country" question
        self.location_select = "81756b9a-5d95-e211-a939-e4115bead28a"
        self.affect_whole_country = "None"
        form = BarrierLocationForm(
            {
                "location_select": self.location_select,
                "affect_whole_country": self.affect_whole_country,
                "admin_areas": self.admin_areas,
                "trading_bloc_EU": self.trading_bloc_EU,
                "trading_bloc_GCC": self.trading_bloc_GCC,
                "trading_bloc_EAEU": self.trading_bloc_EAEU,
                "trading_bloc_Mercosur": self.trading_bloc_Mercosur,
                "barrier-location-affect_whole_country": self.affect_whole_country,
            }
        )

        assert form.is_valid() is False
        expected_error_message = (
            "Select yes if the barrier relates to the entire country"
        )
        assert expected_error_message in form.errors["affect_whole_country"]
