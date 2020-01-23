from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from mock import patch


class EditBarrierTitleTestCase(MarketAccessTestCase):
    def test_edit_title_has_initial_data(self):
        response = self.client.get(
            reverse(
                'barriers:edit_title',
                kwargs={'barrier_id': self.barrier['id']}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert form.initial['title'] == self.barrier['barrier_title']

    def test_title_cannot_be_empty(self):
        response = self.client.post(
            reverse(
                'barriers:edit_title',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'title': ''},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context['form']
        assert form.is_valid() is False
        assert 'title' in form.errors

    @patch("utils.api_client.Resource.patch")
    def test_edit_title_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                'barriers:edit_title',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'title': 'New Title'},
        )
        mock_patch.assert_called_with(
            id=self.barrier['id'],
            barrier_title="New Title",
        )
        assert response.status_code == HTTPStatus.FOUND
