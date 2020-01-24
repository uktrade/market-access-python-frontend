from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from mock import patch


class EditTitleTestCase(MarketAccessTestCase):
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

    @patch("utils.api_client.Resource.patch")
    def test_title_cannot_be_empty(self, mock_patch):
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
        assert mock_patch.called is False

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


class EditDescriptionTestCase(MarketAccessTestCase):
    def test_edit_description_has_initial_data(self):
        response = self.client.get(
            reverse(
                'barriers:edit_description',
                kwargs={'barrier_id': self.barrier['id']}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert (
            form.initial['description'] == self.barrier['problem_description']
        )

    @patch("utils.api_client.Resource.patch")
    def test_description_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                'barriers:edit_description',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'description': ''},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context['form']
        assert form.is_valid() is False
        assert 'description' in form.errors
        assert mock_patch.called is False

    @patch("utils.api_client.Resource.patch")
    def test_edit_description_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                'barriers:edit_description',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'description': 'New description'},
        )
        mock_patch.assert_called_with(
            id=self.barrier['id'],
            problem_description="New description",
        )
        assert response.status_code == HTTPStatus.FOUND
