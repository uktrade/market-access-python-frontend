import logging
from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, List, Optional

# from sentry_sdk import capture_message
import sentry_sdk

logger = logging.getLogger(__name__)


@dataclass
class CompanyHouseAddress(object):
    """Company House Address"""

    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    care_of_name: Optional[str] = None
    country: Optional[str] = None
    locality: Optional[str] = None
    po_box: Optional[str] = None
    postal_code: Optional[str] = None
    premises: Optional[str] = None
    region: Optional[str] = None

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
    company_number: str
    links: Dict[str, str]
    type: str
    date_of_creation: date

    # Fields that are supposed to be required, but can be missing from
    # the dataset
    company_status: Optional[str] = None

    # Optional fields that are not always present
    registered_office_address: Optional[CompanyHouseAddress] = None
    accounts: Optional[dict] = None
    sic_codes: Optional[List[str]] = None
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
    external_registration_number: Optional[int] = None
    super_secure_managing_officer_count: Optional[int] = None

    def __post_init__(self):
        if self.registered_office_address:
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
        if self.registered_office_address:
            return self.registered_office_address.display
        else:
            return


@dataclass
class CompanyHouseSearchResultItem(object):
    """Company House search result item"""

    # Required fields as per companies-house api documentation
    title: str
    kind: str
    address: CompanyHouseAddress
    company_number: str
    company_type: str
    company_status: str
    links: dict
    # input str format YYYY-MM-DD
    date_of_creation: Optional[date] = None

    # Optional fields as per companies-house api documentation
    description: Optional[str] = None
    address_snippet: Optional[str] = None
    description_identifier: Optional[List[str]] = None
    matches: Optional[dict] = None
    snippet: Optional[str] = None
    # input str format YYYY-MM-DD
    date_of_cessation: Optional[date] = None
    external_registration_number: Optional[int] = None

    def __post_init__(self):
        if self.address:
            self.address = CompanyHouseAddress(**self.address)
        if self.date_of_cessation == "Unknown":
            self.date_of_cessation = None

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
        if self.address:
            return self.address.display
        else:
            return


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
        item_list = []
        for item in self.items:
            try:
                formatted_item = CompanyHouseSearchResultItem(**item)
            except Exception as err:
                # We don't want to raise an error for the user, but letting
                # us know via sentry that there could potentially be problems
                # with a change in companies house api data structure is useful
                sentry_sdk.capture_message(
                    f"Problem detected with companies house data, check company: {item['title']} with error: {err}",
                    "error",
                )
                continue
            item_list.append(formatted_item)
        self.items = item_list
