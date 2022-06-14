from django import forms

from utils.api.client import MarketAccessAPIClient


class CompanySearchForm(forms.Form):
    query = forms.CharField(
        label="Find details of the company affected",
        max_length=255,
        error_messages={
            "max_length": "Company should be %(limit_value)d characters or fewer",
            "required": "Enter a company or organisation affected by the barrier",
        },
    )


class AddCompanyForm(forms.Form):
    company_id = forms.CharField()

    def clean_company_id(self):
        return str(self.cleaned_data["company_id"])


class EditCompaniesForm(forms.Form):
    companies = forms.MultipleChoiceField(
        label="",
        choices=[],
        widget=forms.MultipleHiddenInput(),
        required=False,
    )

    def __init__(self, barrier_id, companies, *args, **kwargs):
        self.token = kwargs.pop("token")
        self.barrier_id = barrier_id
        super().__init__(*args, **kwargs)
        self.fields["companies"].choices = [
            (company["id"], company["name"]) for company in companies
        ]

    def clean_companies(self):
        return [
            {"id": id, "name": name}
            for id, name in self.fields["companies"].choices
            if id in self.cleaned_data["companies"]
        ]

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.barrier_id,
            companies=self.cleaned_data["companies"],
        )
