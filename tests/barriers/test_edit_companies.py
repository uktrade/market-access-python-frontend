from http import HTTPStatus

from django.urls import reverse

from barriers.models import Company
from core.tests import MarketAccessTestCase

from mock import patch


class EditCompaniesTestCase(MarketAccessTestCase):
    company_id = "0692683e-5197-4853-a0fe-e43e35b8e7c5"
    company_name = "Test Company"
    company_data = {
        'id': company_id,
        'name': company_name,
        'created_on': '2020-01-01',
        'address': {
            'line_1': "123 Test Street",
            'town': "London",
        },
    }

    def test_edit_companies_landing_page(self):
        """
        Landing page should have the barrier's companies in the form
        """
        response = self.client.get(
            reverse(
                'barriers:edit_companies',
                kwargs={'barrier_id': self.barrier['id']}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        company_ids = [company['id'] for company in self.barrier['companies']]
        assert response.context['form'].initial['companies'] == company_ids
        assert self.client.session['companies'] == self.barrier['companies']

    def test_company_search_page_loads(self):
        """
        The search page should load with a form in the context
        """
        response = self.client.get(
            reverse(
                'barriers:search_company',
                kwargs={'barrier_id': self.barrier['id']}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context

    @patch("utils.datahub.DatahubClient.post")
    def test_company_search_submit(self, mock_post):
        """
        Searching should call the Datahub API
        """
        mock_post.return_value = {
            'count': 1,
            'results': [self.company_data],
        }
        response = self.client.post(
            reverse(
                'barriers:search_company',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'query': "test search"},
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        assert 'results' in response.context
        results = response.context['results']
        assert results['count'] == 1
        assert results['results'][0].id == self.company_id
        assert results['results'][0].name == self.company_name

    @patch("barriers.views.companies.DatahubClient.get_company")
    def test_company_detail(self, mock_get_company):
        """
        Company Detail should call the Datahub API
        """
        mock_get_company.return_value = Company(self.company_data)
        response = self.client.get(
            reverse(
                'barriers:company_detail',
                kwargs={
                    'barrier_id': self.barrier['id'],
                    'company_id': self.company_id,
                }
            ),
        )
        assert response.status_code == HTTPStatus.OK
        mock_get_company.assert_called_with(self.company_id)
        assert response.context['company'].id == self.company_id
        assert response.context['company'].name == self.company_name

    @patch("utils.api.resources.APIResource.patch")
    @patch("barriers.views.companies.DatahubClient.get_company")
    def test_add_company(self, mock_get_company, mock_patch):
        """
        Add company should change the session, not call the API
        """
        mock_get_company.return_value = Company(self.company_data)
        response = self.client.post(
            reverse(
                'barriers:company_detail',
                kwargs={
                    'barrier_id': self.barrier['id'],
                    'company_id': self.company_id,
                }
            ),
            data={'company_id': self.company_id},
        )
        assert response.status_code == HTTPStatus.FOUND
        new_company = {
            'id': self.company_id,
            'name': self.company_name,
        }
        assert new_company in self.client.session['companies']
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_remove_company(self, mock_patch):
        """
        Removing a company should remove it from the session, not call the API
        """
        companies = [
            {
                'id': self.company_id,
                'name': self.company_name,
            }, {
                'id': self.barrier['companies'][0]['id'],
                'name': self.barrier['companies'][0]['name'],
            },
        ]
        self.update_session({'companies': companies})

        response = self.client.post(
            reverse(
                'barriers:remove_company',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'company_id': self.company_id}
        )
        assert response.status_code == HTTPStatus.FOUND
        companies = self.client.session['companies']
        assert {
            'id': self.company_id,
            'name': self.company_name,
        } not in self.client.session['companies']
        assert self.barrier['companies'][0] in self.client.session['companies']
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_confirm_companies(self, mock_patch):
        """
        Saving should call the API
        """
        self.update_session({
            'companies': [{
                'id': self.company_id,
                'name': self.company_name,
            }]
        })

        response = self.client.post(
            reverse(
                'barriers:edit_companies_session',
                kwargs={
                    'barrier_id': self.barrier['id'],
                }
            ),
            data={'companies': [self.company_id]},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.barrier['id'],
            companies=[{
                'id': self.company_id,
                'name': self.company_name,
            }],
        )
        assert 'companies' not in self.client.session
