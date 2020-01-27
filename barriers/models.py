import copy
from urllib.parse import urlencode

from .forms.search import BarrierSearchForm
from interactions.models import Document

from utils.metadata import get_metadata
from utils.models import APIModel

import dateutil.parser


class Barrier(APIModel):
    _admin_areas = None
    _country = None
    _location = None
    _metadata = None
    _sectors = None
    _status = None
    _types = None

    def __init__(self, data):
        self.data = data

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = get_metadata()
        return self._metadata

    @property
    def admin_area_ids(self):
        return self.data['country_admin_areas']

    @property
    def admin_areas(self):
        if self._admin_areas is None:
            self._admin_areas = self.metadata.get_admin_areas(
                self.admin_area_ids
            )
        return self._admin_areas

    @property
    def country(self):
        if self._country is None and self.export_country:
            self._country = self.metadata.get_country(self.export_country)
        return self._country

    @property
    def created_on(self):
        return dateutil.parser.parse(self.data['created_on'])

    @property
    def eu_exit_related_text(self):
        return self.metadata.get_eu_exit_related_text(self.eu_exit_related)

    @property
    def location(self):
        if self._location is None:
            self._location = self.metadata.get_location(
                self.data['export_country'],
                self.data['country_admin_areas']
            )
        return self._location

    @property
    def modified_on(self):
        return dateutil.parser.parse(self.data['modified_on'])

    @property
    def problem_status_text(self):
        return self.metadata.get_problem_status(self.data['problem_status'])

    @property
    def reported_on(self):
        return dateutil.parser.parse(self.data['reported_on'])

    @property
    def sectors(self):
        if self._sectors is None:
            self._sectors = [
                self.metadata.get_sector(sector_id)
                for sector_id in self.sector_ids
            ]
        return self._sectors

    @property
    def sector_ids(self):
        return self.data['sectors'] or []

    @property
    def sector_names(self):
        if self.sectors:
            return [sector.get('name', "Unknown") for sector in self.sectors]
        return ["All sectors"]

    @property
    def source_name(self):
        return self.metadata.get_source(self.source)

    @property
    def status(self):
        if self._status is None:
            status_id = str(self.data['status']['id'])
            self._status = self.metadata.get_status(status_id)
            self._status.update(self.data['status'])
            self._status['date'] = dateutil.parser.parse(self._status['date'])
        return self._status

    @property
    def title(self):
        return self.barrier_title

    @property
    def types(self):
        if self._types is None:
            self._types = [
                self.metadata.get_barrier_type(barrier_type)
                for barrier_type in self.data['barrier_types']
            ]
        return self._types

    @property
    def is_resolved(self):
        return self.status['id'] == '4'

    @property
    def is_partially_resolved(self):
        return self.status['id'] == '3'

    @property
    def is_open(self):
        return self.status['id'] == '2'

    @property
    def is_hibernated(self):
        return self.status['id'] == '5'


class Company(APIModel):
    def __init__(self, data):
        self.data = data
        self.created_on = dateutil.parser.parse(data['created_on'])

    def get_address_display(self):
        address_parts = [
            self.data['address'].get('line_1'),
            self.data['address'].get('line_2'),
            self.data['address'].get('town'),
            self.data['address'].get('county'),
            self.data['address'].get('postcode'),
            self.data['address'].get('country', {}).get('name'),
        ]
        address_parts = [part for part in address_parts if part]
        return ", ".join(address_parts)


class Assessment(APIModel):
    def __init__(self, data):
        self.data = data
        metadata = get_metadata()
        self.impact_text = metadata.get_impact_text(self.data.get('impact'))
        self.documents = [Document(document) for document in data['documents']]


class Watchlist:
    _readable_filters = None

    def __init__(self, name, filters, *args, **kwargs):
        self.name = name
        self.filters = self.clean_filters(filters)

    def clean_filters(self, filters):
        """
        Node saves the watchlist search term as a list for some reason.

        We also use created_by instead of createdBy.
        """
        if 'search' in filters and isinstance(filters['search'], list):
            try:
                filters['search'] = filters['search'][0]
            except IndexError:
                filters['search'] = ""
        if 'createdBy' in filters:
            filters['created_by'] = filters.pop('createdBy')
        return filters

    def to_dict(self):
        return {
            'name': self.name,
            'filters': self.filters,
        }

    @property
    def readable_filters(self):
        if self._readable_filters is None:
            search_form = BarrierSearchForm(
                metadata=get_metadata(),
                data=self.filters,
            )
            search_form.full_clean()
            self._readable_filters = search_form.get_readable_filters()
        return self._readable_filters

    @property
    def querystring(self):
        return urlencode(self.filters, doseq=True)

    def get_api_params(self):
        """
        Transform watchlist filters into api parameters
        """
        filters = copy.deepcopy(self.filters)
        region = filters.pop('region', [])
        country = filters.pop('country', [])

        if country or region:
            filters['location'] = country + region

        created_by = (
            filters.pop('createdBy', []) + filters.pop('created_by', [])
        )
        if '1' in created_by:
            filters['user'] = 1
        elif '2' in created_by:
            filters['team'] = 1

        filter_map = {
            'type': 'barrier_type',
            'search': 'text',
        }

        api_params = {}
        for name, value in filters.items():
            mapped_name = filter_map.get(name, name)
            if isinstance(value, list):
                api_params[mapped_name] = ",".join(value)
            else:
                api_params[mapped_name] = value

        return api_params
