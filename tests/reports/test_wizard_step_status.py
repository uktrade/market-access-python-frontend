# CASES TO TEST #
#
# 3. Continue with an invalid format for month (partially resolved date field)
#    triggers error
#
# 4. Continue with an invalid format for year (partially resolved date field)
#    triggers error
#
# 5. Continue with an invalid format for month (resolved date field)
#    triggers error
#
# 6. Continue with an invalid format for year (resolved date field)
#    triggers error
#
# 7. Continue with an invalid format for month (start date field)
#    triggers error
#
# 8. Continue with an invalid format for year (start date field)
#    triggers error
#

import datetime
import logging

from core.tests import MarketAccessTestCase
from reports.report_barrier_forms import BarrierStatusForm

logger = logging.getLogger(__name__)


class ReportWizardStatusStepTestCase(MarketAccessTestCase):
    # make django-test path=reports/test_wizard_step_status.py::ReportWizardStatusStepTestCase

    def setUp(self):
        # Dummy data which can be overridden by individual tests
        self.test_status = "2"
        self.test_partially_resolved_date = "01 2023"
        self.test_partially_resolved_description = (
            "This is a partially resolved description"
        )
        self.test_resolved_date = "01 2023"
        self.test_resolved_description = "This is a fully resolved description"
        self.test_start_date_unknown = None
        self.test_start_date = "01 2023"
        self.test_currently_active = "YES"

    def test_valid_form_entry_open_and_start_date(self):
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid()

        # Open status takes todays date for status date
        todays_date = datetime.date.today()
        assert form.cleaned_data["status_date"] == todays_date
        assert form.cleaned_data["status_summary"] == ""

        # When start date is given, this ends up in cleaned_data
        input_month = int(self.test_start_date.split()[0])
        input_year = int(self.test_start_date.split()[1])
        assert form.cleaned_data["start_date"] == datetime.date(input_year, input_month, 1)
        assert form.cleaned_data["start_date_known"] is True
        # If start date is in the past, currently active is automatically set
        assert form.cleaned_data["is_currently_active"] is True

    def test_valid_form_entry_partially_resolved_and_unknown_active_date(self):
        self.test_status = "3"
        self.test_start_date_unknown = True
        self.test_start_date = None
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid()

        # Partially Resolved status takes given date for status date
        input_month = int(self.test_partially_resolved_date.split()[0])
        input_year = int(self.test_partially_resolved_date.split()[1])
        assert form.cleaned_data["status_date"] == datetime.date(input_year, input_month, 1)
        assert form.cleaned_data["status_summary"] == self.test_partially_resolved_description

        # When start date unknown is set, we expect these values for start date
        assert form.cleaned_data["start_date"] is None
        assert form.cleaned_data["start_date_known"] is False
        assert form.cleaned_data["is_currently_active"] == self.test_currently_active

    def test_valid_form_entry_resolved_and_start_date_in_future(self):
        self.test_status = "4"
        self.test_start_date = "01 2099"
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid()

        # Resolved status takes given date for status date
        input_month = int(self.test_resolved_date.split()[0])
        input_year = int(self.test_resolved_date.split()[1])
        assert form.cleaned_data["status_date"] == datetime.date(input_year, input_month, 1)
        assert form.cleaned_data["status_summary"] == self.test_resolved_description

        # When start date is given, this ends up in cleaned_data
        input_month = int(self.test_start_date.split()[0])
        input_year = int(self.test_start_date.split()[1])
        assert form.cleaned_data["start_date"] == datetime.date(input_year, input_month, 1)
        assert form.cleaned_data["start_date_known"] is True
        # If start date is in the future, currently active is automatically set
        assert form.cleaned_data["is_currently_active"] is False

    def test_error_no_status_selected(self):
        self.test_status = None
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Select barrier status"
        assert expected_error_message in form.errors["status"]

    def test_error_too_old_partially_resolved_date(self):
        self.test_status = "3"
        self.test_partially_resolved_date = "12 1980"
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Date must be after 1990"
        assert expected_error_message in form.errors["partially_resolved_date"]

    def test_error_far_future_partially_resolved_date(self):
        self.test_status = "3"
        self.test_partially_resolved_date = "12 2442"
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Date must be before 2100"
        assert expected_error_message in form.errors["partially_resolved_date"]

    def test_error_too_old_resolved_date(self):
        self.test_status = "4"
        self.test_resolved_date = "12 1980"
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Date must be after 1990"
        assert expected_error_message in form.errors["resolved_date"]

    def test_error_far_future_resolved_date(self):
        self.test_status = "4"
        self.test_resolved_date = "12 2442"
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Date must be before 2100"
        assert expected_error_message in form.errors["resolved_date"]

    def test_error_too_old_start_date(self):
        self.test_status = "2"
        self.test_start_date = "12 1980"
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Date must be after 1990"
        assert expected_error_message in form.errors["start_date"]

    def test_error_far_future_start_date(self):
        self.test_status = "2"
        self.test_start_date = "12 2442"
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Date must be before 2100"
        assert expected_error_message in form.errors["start_date"]

    def test_error_partially_resolved_date_missing(self):
        self.test_status = "3"
        self.test_partially_resolved_date = None
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Enter a date the barrier was partially resolved"
        assert expected_error_message in form.errors["partially_resolved_date"]

    def test_error_partially_resolved_description_missing(self):
        self.test_status = "3"
        self.test_partially_resolved_description = None
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Enter a description"
        assert expected_error_message in form.errors["partially_resolved_description"]

    def test_error_resolved_date_missing(self):
        self.test_status = "4"
        self.test_resolved_date = None
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Enter a date the barrier was resolved"
        assert expected_error_message in form.errors["resolved_date"]

    def test_error_resolved_description_missing(self):
        self.test_status = "4"
        self.test_resolved_description = None
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Enter a description"
        assert expected_error_message in form.errors["resolved_description"]

    def test_error_start_date_and_dont_know_missing(self):
        self.test_start_date = None
        self.test_start_date_unknown = None
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Enter a date or select 'I don't know'."
        assert expected_error_message in form.errors["start_date"]

    def test_error_start_date_and_dont_know_both_entered(self):
        self.test_start_date_unknown = True
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Enter a date or select 'I don't know'."
        assert expected_error_message in form.errors["start_date"]

    def test_error_dont_know_currently_active_missing(self):
        self.test_start_date = None
        self.test_start_date_unknown = True
        self.test_currently_active = None
        form = BarrierStatusForm(
            {
                "status": self.test_status,
                "partially_resolved_date": self.test_partially_resolved_date,
                "partially_resolved_description": self.test_partially_resolved_description,
                "resolved_date": self.test_resolved_date,
                "resolved_description": self.test_resolved_description,
                "start_date_unknown": self.test_start_date_unknown,
                "start_date": self.test_start_date,
                "currently_active": self.test_currently_active,
            }
        )

        assert form.is_valid() is False
        expected_error_message = (
            "Select yes if the barrier is currently affecting trade"
        )
        assert expected_error_message in form.errors["currently_active"]
