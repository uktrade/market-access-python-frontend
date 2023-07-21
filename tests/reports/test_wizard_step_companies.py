# CASES TO TEST #

# 4. Error - Continue with no companies added

import logging

from core.tests import MarketAccessTestCase
from reports.report_barrier_forms import BarrierCompaniesAffectedForm

logger = logging.getLogger(__name__)


class ReportWizardCompaniesStepTestCase(MarketAccessTestCase):
    # make django-test path=reports/test_wizard_step_companies.py::ReportWizardCompaniesStepTestCase

    def setUp(self):
        # Dummy data which can be overridden by individual tests
        self.companies_affected = """[
            {
                "company_number":"12345",
                "title":"COMPANY HOUSE CO",
                "date_of_creation":"2000-05-06",
                "address_snippet":"29 Aurelia Road, Croydon, CR0 3BE",
                "company_status":"active"
            }
        ]"""
        self.unrecognised_company = """[
            "Unrecognised company number 1",
            "Unrecognised company number 2"
        ]"""

    def test_valid_form_entry_company_and_other_orgs(self):
        form = BarrierCompaniesAffectedForm(
            {
                "companies_affected": self.companies_affected,
                "unrecognised_company": self.unrecognised_company,
            }
        )

        assert form.is_valid()
        assert form.cleaned_data["companies"] == [
            {"id": "12345", "name": "COMPANY HOUSE CO"}
        ]
        assert form.cleaned_data["related_organisations"] == [
            {"id": "", "name": "Unrecognised company number 1"},
            {"id": "", "name": "Unrecognised company number 2"},
        ]

    def test_valid_form_entry_company_only(self):
        self.unrecognised_company = None
        form = BarrierCompaniesAffectedForm(
            {
                "companies_affected": self.companies_affected,
                "unrecognised_company": self.unrecognised_company,
            }
        )

        assert form.is_valid()
        assert form.cleaned_data["companies"] == [
            {"id": "12345", "name": "COMPANY HOUSE CO"}
        ]
        assert form.cleaned_data["related_organisations"] == []

    def test_valid_form_entry_other_organisations_only(self):
        self.companies_affected = "None"
        form = BarrierCompaniesAffectedForm(
            {
                "companies_affected": self.companies_affected,
                "unrecognised_company": self.unrecognised_company,
            }
        )

        assert form.is_valid()
        assert form.cleaned_data["companies"] == []
        assert form.cleaned_data["related_organisations"] == [
            {"id": "", "name": "Unrecognised company number 1"},
            {"id": "", "name": "Unrecognised company number 2"},
        ]

    def test_error_missing_companies_and_other_organisations(self):
        self.companies_affected = "None"
        self.unrecognised_company = None
        form = BarrierCompaniesAffectedForm(
            {
                "companies_affected": self.companies_affected,
                "unrecognised_company": self.unrecognised_company,
            }
        )

        assert form.is_valid() is False
        expected_error_message = "Add all companies affected by the barrier"
        assert expected_error_message in str(form.errors["companies_affected"])
