from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional


@dataclass
class CompanyHouseAddress(object):
    """Company House Address"""

    address_line_1: str
    locality: str
    postal_code: Optional[str] = None
    address_line_2: Optional[str] = None
    premises: Optional[str] = None
    care_of_name: Optional[str] = None
    care_of: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None

    @property
    def display(self):
        address_parts = [
            self.address_line_1,
            self.address_line_2,
            self.locality,
            self.region,
            self.postal_code,
            self.country,
        ]

        return ", ".join(filter(lambda x: x is not None, address_parts))


@dataclass
class CompanyHouseCompany(object):
    """
    Company House - Company

    Note: Date strings are in format YYYY-MM-DD
    """

    # Required fields
    company_name: str
    company_status: str
    registered_office_address: CompanyHouseAddress
    company_number: str
    links: Dict[str, str]
    accounts: dict
    type: str
    sic_codes: List[str]
    date_of_creation: date

    # Optional fields that are not always present
    date_of_cessation: Optional[date] = None
    annual_return: Optional[dict] = None
    branch_company_details: Optional[dict] = None
    company_status_detail: Optional[str] = None
    confirmation_statement: Optional[dict] = None
    foreign_company_details: Optional[dict] = None
    has_been_liquidated: Optional[bool] = None
    has_charges: Optional[bool] = None
    has_insolvency_history: Optional[bool] = None
    is_community_interest_company: Optional[bool] = None
    jurisdiction: Optional[str] = None
    last_full_members_list_date: Optional[date] = None
    previous_company_names: Optional[List[dict]] = None
    registered_office_is_in_dispute: Optional[bool] = None
    service_address: Optional[CompanyHouseAddress] = None
    undeliverable_registered_office_address: Optional[bool] = None
    status: Optional[str] = None
    etag: Optional[str] = None
    can_file: Optional[bool] = None
    has_super_secure_pscs: Optional[bool] = None

    def __post_init__(self):
        self.registered_office_address = CompanyHouseAddress(
            **self.registered_office_address
        )
        if self.date_of_creation:
            self.date_of_creation = datetime.strptime(
                self.date_of_creation, "%Y-%m-%d"
            ).date()
        if self.date_of_cessation:
            self.date_of_cessation = datetime.strptime(
                self.date_of_cessation, "%Y-%m-%d"
            ).date()
        if self.last_full_members_list_date:
            self.last_full_members_list_date = datetime.strptime(
                self.last_full_members_list_date, "%Y-%m-%d"
            ).date()

    @property
    def id(self):
        return self.company_number

    @property
    def name(self):
        return self.company_name

    @property
    def address_display(self):
        """
        Get company address
        """
        return self.registered_office_address.display


@dataclass
class CompanyHouseSearchResultItem(object):
    """Company House search result item"""

    title: str
    description: str
    kind: str
    address: CompanyHouseAddress
    address_snippet: Optional[str]
    company_number: str
    company_type: str
    description_identifier: List[str]
    company_status: str
    matches: dict

    links: dict
    snippet: str

    # input str format YYYY-MM-DD
    date_of_creation: date
    # input str format YYYY-MM-DD
    date_of_cessation: Optional[date] = None

    def __post_init__(self):
        self.address = CompanyHouseAddress(**self.address)
        if self.date_of_cessation:
            self.date_of_cessation = datetime.strptime(
                self.date_of_cessation, "%Y-%m-%d"
            ).date()
        if self.date_of_creation:
            self.date_of_creation = datetime.strptime(
                self.date_of_creation, "%Y-%m-%d"
            ).date()

    @property
    def id(self):
        return self.company_number

    @property
    def name(self):
        return self.title

    @property
    def address_display(self):
        """
        Get company address
        """
        return self.address.display


@dataclass
class CompanyHouseSearchResult(object):
    """
    Company house search result
    """

    page_number: int
    total_results: int
    start_index: int
    kind: str
    items_per_page: int
    items: List[CompanyHouseCompany]

    def __post_init__(self):
        self.items = [CompanyHouseSearchResultItem(**item) for item in self.items]
