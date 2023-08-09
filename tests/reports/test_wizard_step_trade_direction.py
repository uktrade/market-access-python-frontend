import logging

from core.tests import MarketAccessTestCase
from reports.report_barrier_forms import BarrierTradeDirectionForm

logger = logging.getLogger(__name__)


class ReportWizardTradeDirectionStepTestCase(MarketAccessTestCase):
    # make django-test path=reports/test_wizard_step_trade_direction.py::ReportWizardTradeDirectionStepTestCase

    def test_valid_form_entry(self):
        test_trade_direction = "1"
        form = BarrierTradeDirectionForm(
            {
                "trade_direction": test_trade_direction,
            }
        )

        # Assert is_valid first before running clean so cleaned_data is set
        assert form.is_valid()
        assert test_trade_direction in form.cleaned_data["trade_direction"]

    def test_invalid_form_entry(self):
        test_trade_direction = "4"
        form = BarrierTradeDirectionForm(
            {
                "trade_direction": test_trade_direction,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Select a valid choice"
        assert expected_error_message in str(form.errors["trade_direction"])

    def test_missing_form_entry(self):
        test_trade_direction = None
        form = BarrierTradeDirectionForm(
            {
                "trade_direction": test_trade_direction,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Select the trade direction this barrier affects"
        assert expected_error_message in form.errors["trade_direction"]
