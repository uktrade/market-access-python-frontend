# CASES TO TEST #
#
# 5. Test that save and exit saves when title has been given value
#
# 6. Test that save and exit does not save when no details entered for title

import logging
import random
import string

from core.tests import MarketAccessTestCase
from reports.report_barrier_forms import BarrierAboutForm

logger = logging.getLogger(__name__)


class ReportWizardAboutStepTestCase(MarketAccessTestCase):
    # make django-test path=reports/test_wizard_step_about.py::ReportWizardAboutStepTestCase

    def test_valid_form_entry(self):

        test_title = "New barrier test title"
        test_summary = "This is the description the the barrier"
        form = BarrierAboutForm(
            {
                "title": test_title,
                "summary": test_summary,
            }
        )

        # Assert is_valid first before running clean so cleaned_data is set
        assert form.is_valid()
        assert test_title in form.cleaned_data["title"]
        assert test_summary in form.cleaned_data["summary"]

    def test_title_too_long_entry(self):

        test_title = "".join(random.choices(string.ascii_letters, k=200))
        test_summary = "This is the description the the barrier"
        form = BarrierAboutForm(
            {
                "title": test_title,
                "summary": test_summary,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Name should be 150 characters or less"
        assert expected_error_message in form.errors["title"]

    def test_title_missing_entry(self):

        test_title = None
        test_summary = "This is the description the the barrier"
        form = BarrierAboutForm(
            {
                "title": test_title,
                "summary": test_summary,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Enter a barrier title"
        assert expected_error_message in form.errors["title"]

    def test_summary_too_long_entry(self):

        test_title = "New barrier test title"
        test_summary = "".join(random.choices(string.ascii_letters, k=400))
        form = BarrierAboutForm(
            {
                "title": test_title,
                "summary": test_summary,
            }
        )

        assert form.is_valid() is False
        expected_error_message = (
            "Ensure this value has at most 300 characters (it has 400)"
        )
        assert expected_error_message in str(form.errors["summary"])

    def test_summary_missing_entry(self):

        test_title = "New barrier test title"
        test_summary = None
        form = BarrierAboutForm(
            {
                "title": test_title,
                "summary": test_summary,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Enter a barrier description"
        assert expected_error_message in form.errors["summary"]
