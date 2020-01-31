from http import HTTPStatus

from django.conf import settings
from django.urls import reverse

from barriers.models import Barrier
from core.tests import MarketAccessTestCase

from utils.models import ModelList

from mock import patch


class DashboardTestCase(MarketAccessTestCase):
    simple_watchlist = {
        'name': 'Simple',
        'filters': {'priority': ['MEDIUM']}
    }
    complex_watchlist = {
        'name': 'Complex',
        'filters': {
            'search': 'Test',
            'country': ['9f5f66a0-5d95-e211-a939-e4115bead28a'],
            'sector': [
                '9538cecc-5f95-e211-a939-e4115bead28a',
                'a538cecc-5f95-e211-a939-e4115bead28a',
            ],
            'type': ['123'],
            'region': ['3e6809d6-89f6-4590-8458-1d0dab73ad1a'],
            'priority': ['HIGH', 'MEDIUM'],
            'status': ['1', '2', '3'],
            'created_by': ['1']
        }
    }

    def set_watchlists(self, *args):
        self.update_session({
            'user_data': {
                'user_profile': {
                    'watchList': {
                        'lists': args
                    }
                }
            }
        })

    def test_empty_watchlists(self):
        response = self.client.get(reverse('barriers:dashboard'))
        assert response.status_code == HTTPStatus.OK
        assert response.context['watchlists'] == []
        assert response.context['barriers'] == []
        assert response.context['can_add_watchlist'] is True

    @patch("utils.api.resources.APIResource.list")
    def test_simple_watchlist(self, mock_list):
        self.set_watchlists(self.simple_watchlist)

        response = self.client.get(reverse('barriers:dashboard'))
        assert response.status_code == HTTPStatus.OK
        assert len(response.context['watchlists']) == 1
        assert response.context['watchlists'][0].name == "Simple"
        mock_list.assert_called_with(
            priority="MEDIUM",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            ordering='-modified_on',
        )

    @patch("utils.api.resources.APIResource.list")
    def test_complex_watchlist(self, mock_list):
        self.set_watchlists(self.complex_watchlist)
        barrier_list = ModelList(
            model=Barrier,
            data=self.barriers,
            total_count=2,
        )
        mock_list.return_value = barrier_list

        response = self.client.get(reverse('barriers:dashboard'))
        assert response.status_code == HTTPStatus.OK
        assert len(response.context['watchlists']) == 1
        assert response.context['watchlists'][0].name == "Complex"
        assert response.context['barriers'] == barrier_list
        assert response.context['can_add_watchlist'] is True
        mock_list.assert_called_with(
            ordering="-modified_on",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            text='Test',
            location=(
                '9f5f66a0-5d95-e211-a939-e4115bead28a,'
                '3e6809d6-89f6-4590-8458-1d0dab73ad1a'
            ),
            sector=(
                '9538cecc-5f95-e211-a939-e4115bead28a,'
                'a538cecc-5f95-e211-a939-e4115bead28a'
            ),
            barrier_type='123',
            priority='HIGH,MEDIUM',
            status='1,2,3',
            user=1,
        )

    @patch("utils.api.resources.APIResource.list")
    def test_tabs(self, mock_list):
        self.set_watchlists(self.complex_watchlist, self.simple_watchlist)

        response = self.client.get(
            reverse('barriers:dashboard'),
            data={'list': '1'}
        )
        assert response.status_code == HTTPStatus.OK
        assert len(response.context['watchlists']) == 2
        assert response.context['selected_watchlist'].name == "Simple"
        assert response.context['can_add_watchlist'] is True

    @patch("utils.api.resources.APIResource.list")
    def test_can_add_watchlist(self, mock_list):
        self.set_watchlists(*[self.simple_watchlist] * 3)

        response = self.client.get(reverse('barriers:dashboard'))
        assert response.status_code == HTTPStatus.OK
        assert len(response.context['watchlists']) == 3
        assert response.context['can_add_watchlist'] is False

    @patch("utils.api.resources.APIResource.list")
    def test_pagination(self, mock_list):
        self.set_watchlists(*[self.simple_watchlist] * 3)
        mock_list.return_value = ModelList(
            model=Barrier,
            data=[self.barrier] * settings.API_RESULTS_LIMIT,
            total_count=87,
        )

        response = self.client.get(
            reverse('barriers:dashboard'),
            data={'page': '7', 'list': '2'},
        )

        assert response.status_code == HTTPStatus.OK

        mock_list.assert_called_with(
            priority="MEDIUM",
            ordering="-modified_on",
            limit=settings.API_RESULTS_LIMIT,
            offset=60,
        )
        barriers = response.context['barriers']
        assert len(barriers) == settings.API_RESULTS_LIMIT
        assert barriers.total_count == 87

        pagination = response.context['pagination']
        assert pagination['total_pages'] == 9
        assert pagination['pages'][0]['label'] == 1
        assert pagination['pages'][0]['url'] == "list=2&page=1"
        page_labels = [page['label'] for page in pagination['pages']]
        assert page_labels == [1, '...', 6, 7, 8, 9]
