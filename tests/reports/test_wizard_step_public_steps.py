import logging
import random
import string

from core.tests import MarketAccessTestCase
from reports.report_barrier_forms import (
    BarrierPublicEligibilityForm,
    BarrierPublicInformationGateForm,
    BarrierPublicSummaryForm,
    BarrierPublicTitleForm,
)

logger = logging.getLogger(__name__)


class ReportWizardPublicEligibilityTestCase(MarketAccessTestCase):
    # make django-test path=reports/test_wizard_step_public_steps.py::ReportWizardPublicEligibilityTestCase

    def test_valid_form_entry(self):
        form = BarrierPublicEligibilityForm(
            {
                "public_eligibility": "yes",
                "public_eligibility_summary": "",
            }
        )

        assert form.is_valid()
        assert form.cleaned_data["public_eligibility"] is True
        assert form.cleaned_data["public_eligibility_summary"] == ""

    def test_valid_form_entry_negative_path(self):
        test_summary = (
            "This is the summary to say why the barrier is not eligible for the public"
        )
        form = BarrierPublicEligibilityForm(
            {
                "public_eligibility": "no",
                "public_eligibility_summary": test_summary,
            }
        )

        assert form.is_valid()
        assert form.cleaned_data["public_eligibility"] is False
        assert test_summary in form.cleaned_data["public_eligibility_summary"]

    def test_invalid_form_missing_summary(self):
        form = BarrierPublicEligibilityForm(
            {
                "public_eligibility": "no",
                "public_eligibility_summary": "",
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Enter a reason for not publishing this barrier"
        assert expected_error_message in str(form.errors["public_eligibility_summary"])

    def test_empty_form(self):
        form = BarrierPublicEligibilityForm(
            {
                "public_eligibility": "",
                "public_eligibility_summary": "",
            }
        )

        assert form.is_valid() is False
        expected_error_message = (
            "Select whether this barrier should be published on GOV.UK, once approved"
        )
        assert expected_error_message in str(form.errors["public_eligibility"])

    def test_valid_form_entry_clears_summary(self):
        test_summary = (
            "This is the summary to say why the barrier is not eligible for the public"
        )
        form = BarrierPublicEligibilityForm(
            {
                "public_eligibility": "yes",
                "public_eligibility_summary": test_summary,
            }
        )

        assert form.is_valid()
        assert form.cleaned_data["public_eligibility"] is True
        assert form.cleaned_data["public_eligibility_summary"] == ""


class ReportWizardPublicInformationGateTestCase(MarketAccessTestCase):
    # make django-test path=reports/test_wizard_step_public_steps.py::ReportWizardPublicInformationGateTestCase

    def test_valid_form_entry(self):
        form = BarrierPublicInformationGateForm(
            {
                "public_information": "true",
            }
        )

        assert form.is_valid()
        assert form.cleaned_data["public_information"] == "true"

    def test_valid_form_entry_negative_path(self):
        form = BarrierPublicInformationGateForm(
            {
                "public_information": "false",
            }
        )

        assert form.is_valid()
        assert form.cleaned_data["public_information"] == "false"

    def test_invalid_form_entry(self):
        form = BarrierPublicInformationGateForm(
            {
                "public_information": "Yea",
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Select a valid choice"
        assert expected_error_message in str(form.errors["public_information"])

    def test_empty_form_entry(self):
        form = BarrierPublicInformationGateForm(
            {
                "public_information": "",
            }
        )

        assert form.is_valid() is False
        expected_error_message = (
            "Select whether you want to publish the barrier now or later"
        )
        assert expected_error_message in str(form.errors["public_information"])


class ReportWizardPublicTitleTestCase(MarketAccessTestCase):
    # make django-test path=reports/test_wizard_step_public_steps.py::ReportWizardPublicTitleTestCase

    def test_valid_form_entry(self):
        form = BarrierPublicTitleForm(
            {
                "title": "Public Title Example",
            }
        )

        assert form.is_valid()
        assert form.cleaned_data["title"] == "Public Title Example"

    def test_invalid_form_empty(self):
        form = BarrierPublicTitleForm(
            {
                "title": "",
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Enter a public title for this barrier"
        assert expected_error_message in str(form.errors["title"])

    def test_invalid_form_too_long(self):
        test_title = "".join(random.choices(string.ascii_letters, k=300))
        form = BarrierPublicTitleForm(
            {
                "title": test_title,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Title should be 255 characters or less"
        assert expected_error_message in str(form.errors["title"])


class ReportWizardPublicSummaryTestCase(MarketAccessTestCase):
    # make django-test path=reports/test_wizard_step_public_steps.py::ReportWizardPublicSummaryTestCase

    def test_valid_form_entry(self):
        form = BarrierPublicSummaryForm(
            {
                "summary": "Public summary example",
            }
        )

        assert form.is_valid()
        assert form.cleaned_data["summary"] == "Public summary example"

    def test_invalid_form_empty(self):
        form = BarrierPublicSummaryForm(
            {
                "summary": "",
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Enter a public summary for this barrier"
        assert expected_error_message in str(form.errors["summary"])

    def test_invalid_form_too_long(self):
        test_summary = "".join(random.choices(string.ascii_letters, k=2001))
        form = BarrierPublicSummaryForm(
            {
                "summary": test_summary,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Summary should be 1500 characters or less"
        assert expected_error_message in str(form.errors["summary"])
