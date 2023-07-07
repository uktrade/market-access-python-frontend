import json
import logging

from django import forms

from utils.api.client import MarketAccessAPIClient

logger = logging.getLogger(__name__)


class CompanySearchForm(forms.Form):
    query = forms.CharField(
        label="Find the affected company",
        max_length=255,
        error_messages={
            "max_length": "Entry should be %(limit_value)d characters or less",
            "required": "Enter a company name, address or number",
        },
    )


class AddCompanyForm(forms.Form):
    company_id = forms.CharField()

    def clean_company_id(self):
        return str(self.cleaned_data["company_id"])


class EditCompaniesForm(forms.Form):
    companies_affected = forms.CharField(
        label="Name of company affected by the barrier",
        help_text=(
            "Add at least one company. You can search by name, address or company number"
        ),
        widget=forms.HiddenInput(),
    )
    unrecognised_company = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()

        # Convert the passed companies string to list of dictionaries
        companies_list = []
        if cleaned_data["companies_affected"] != "None":
            companies_list = json.loads(cleaned_data["companies_affected"])
        added_companies_list = []
        if cleaned_data["unrecognised_company"] != "":
            added_companies_list = json.loads(cleaned_data["unrecognised_company"])

        # Need to error if none detected in lists
        if companies_list == [] and added_companies_list == []:
            msg = "Add all companies affected by the barrier."
            self.add_error("companies_affected", msg)

        # Setup list to contain the cleaned company information
        cleaned_companies_list = []
        cleaned_added_companies_list = []

        # Loop the passed companies, get their ID and name,
        # put them into a dict and append to the list
        for company in companies_list:
            cleaned_company = {
                "id": company["company_number"],
                "name": company["title"],
            }
            cleaned_companies_list.append(cleaned_company)

        # Loop through added companies and convert the string in the existing
        # data to objects
        for company in added_companies_list:
            cleaned_company = {"id": "", "name": company}
            cleaned_added_companies_list.append(cleaned_company)

        # Update cleaned_data
        cleaned_data["companies"] = cleaned_companies_list
        cleaned_data["related_organisations"] = cleaned_added_companies_list

        return cleaned_data

    def save(self, barrier_id, token):
        client = MarketAccessAPIClient(token)
        client.barriers.patch(
            id=barrier_id,
            companies=self.cleaned_data["companies"],
            related_organisations=self.cleaned_data["related_organisations"],
        )
