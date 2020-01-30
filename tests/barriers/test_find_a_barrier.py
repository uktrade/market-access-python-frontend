from http import HTTPStatus

from django.conf import settings
from django.urls import reverse

from barriers.models import Barrier
from core.tests import MarketAccessTestCase
from utils.metadata import get_metadata
from utils.models import ModelList

from mock import patch


class FindABarrierTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.APIResource.list")
    def test_empty_search(self, mock_list):
        response = self.client.get(reverse('barriers:find_a_barrier'))
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported_on",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
        )

    @patch("utils.api.resources.APIResource.list")
    def test_search_form_choices(self, mock_list):
        response = self.client.get(reverse('barriers:find_a_barrier'))
        assert response.status_code == HTTPStatus.OK

        form = response.context['form']

        metadata = get_metadata()
        country_list = metadata.get_country_list()
        country_choices = form.fields['country'].choices
        assert len(country_choices) == len(country_list) + 1

        sector_list = metadata.get_sector_list(level=0)
        sector_choices = form.fields['sector'].choices
        assert len(sector_choices) == len(sector_list) + 1

        type_list = set(
            [type['id'] for type in metadata.data['barrier_types']]
        )
        type_choices = form.fields['type'].choices
        assert len(type_choices) == len(type_list) + 1

        region_list = set(
            [region['id'] for region in metadata.get_overseas_region_list()]
        )
        region_choices = form.fields['region'].choices
        assert len(region_choices) == len(region_list) + 1

        priority_list = metadata.data['barrier_priorities']
        priority_choices = form.fields['priority'].choices
        assert len(priority_choices) == len(priority_list)

        status_choices = form.fields['status'].choices
        assert len(status_choices) == 6

        created_by_choices = form.fields['created_by'].choices
        assert len(created_by_choices) == 2

    @patch("utils.api.resources.APIResource.list")
    def test_search_filters(self, mock_list):
        response = self.client.get(
            reverse('barriers:find_a_barrier'),
            data={
                'search': "Test search",
                'country': [
                    "9f5f66a0-5d95-e211-a939-e4115bead28a",
                    "83756b9a-5d95-e211-a939-e4115bead28a",
                ],
                'sector': [
                    "9538cecc-5f95-e211-a939-e4115bead28a",
                    "aa22c9d2-5f95-e211-a939-e4115bead28a",
                ],
                'type': ['130', '141'],
                'region': [
                    "3e6809d6-89f6-4590-8458-1d0dab73ad1a",
                    "5616ccf5-ab4a-4c2c-9624-13c69be3c46b",
                ],
                'priority': ["HIGH", "MEDIUM"],
                'status': ['1', '2', '7'],
                'created_by': [1],
            }
        )
        assert response.status_code == HTTPStatus.OK

        form = response.context['form']
        assert form.cleaned_data['search'] == "Test search"
        assert form.cleaned_data['country'] == [
            '9f5f66a0-5d95-e211-a939-e4115bead28a',
            '83756b9a-5d95-e211-a939-e4115bead28a',
        ]
        assert form.cleaned_data['sector'] == [
            '9538cecc-5f95-e211-a939-e4115bead28a',
            'aa22c9d2-5f95-e211-a939-e4115bead28a',
        ]
        assert form.cleaned_data['type'] == ['130', '141']
        assert form.cleaned_data['region'] == [
            '3e6809d6-89f6-4590-8458-1d0dab73ad1a',
            '5616ccf5-ab4a-4c2c-9624-13c69be3c46b',
        ]
        assert form.cleaned_data['priority'] == ['HIGH', 'MEDIUM']
        assert form.cleaned_data['status'] == ['1', '2', '7']
        assert form.cleaned_data['created_by'] == ['1']

        mock_list.assert_called_with(
            ordering="-reported_on",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            text='Test search',
            location=(
                '9f5f66a0-5d95-e211-a939-e4115bead28a,'
                '83756b9a-5d95-e211-a939-e4115bead28a,'
                '3e6809d6-89f6-4590-8458-1d0dab73ad1a,'
                '5616ccf5-ab4a-4c2c-9624-13c69be3c46b'
            ),
            sector=(
                '9538cecc-5f95-e211-a939-e4115bead28a,'
                'aa22c9d2-5f95-e211-a939-e4115bead28a'
            ),
            barrier_type='130,141',
            priority='HIGH,MEDIUM',
            status='1,2,7',
            user='1',
        )

    @patch("utils.api.resources.APIResource.list")
    def test_created_by_fitler(self, mock_list):
        response = self.client.get(
            reverse('barriers:find_a_barrier'),
            data={'created_by': ['1']},
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported_on",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            user='1',
        )

        response = self.client.get(
            reverse('barriers:find_a_barrier'),
            data={'created_by': ['2']},
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported_on",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            team='1',
        )

        response = self.client.get(
            reverse('barriers:find_a_barrier'),
            data={'created_by': ['1', '2']},
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported_on",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            team='1',
        )

    @patch("utils.api.resources.APIResource.list")
    def test_pagination(self, mock_list):
        mock_list.return_value = ModelList(
            model=Barrier,
            data=[self.barrier] * 10,
            total_count=123,
        )

        response = self.client.get(
            reverse('barriers:find_a_barrier'),
            data={'status': ['1', '2', '3', '4', '5'], 'page': '6'},
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            ordering="-reported_on",
            limit=10,
            offset=50,
            status='1,2,3,4,5',
        )
        barriers = response.context['barriers']
        assert len(barriers) == 10
        assert barriers.total_count == 123

        pagination = response.context['pagination']
        assert pagination['total_pages'] == 13
        assert pagination['pages'][0]['label'] == 1
        assert pagination['pages'][0]['url'] == (
            "status=1&status=2&status=3&status=4&status=5&page=1"
        )
        page_labels = [page['label'] for page in pagination['pages']]
        assert page_labels == [1, '...', 5, 6, 7, 8, '...', 13]
