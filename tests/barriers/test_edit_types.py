from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from mock import patch


class EditBarrierTypesTestCase(MarketAccessTestCase):
    def test_edit_types_landing_page(self):
        """
        Landing page should load the barrier's types into the session
        """
        response = self.client.get(
            reverse(
                'barriers:edit_types',
                kwargs={'barrier_id': self.barrier['id']}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert form.initial['barrier_types'] == self.barrier['barrier_types']

        session_barrier_type_ids = [
            type['id'] for type in self.client.session['barrier_types']
        ]
        assert session_barrier_type_ids == self.barrier['barrier_types']

    def test_add_type_choices(self):
        """
        Add type page should not include current types in choices
        """
        self.update_session({
            'barrier_types': [
                {
                    'id': type_id,
                    'title': "Title",
                } for type_id in self.barrier['barrier_types']
            ],
        })

        response = self.client.get(
            reverse(
                'barriers:add_type',
                kwargs={'barrier_id': self.barrier['id']}
            ),
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        choice_values = [k for k, v in form.fields['barrier_type'].choices]

        for type_id in self.barrier['barrier_types']:
            assert type_id not in choice_values

    @patch("utils.api_client.Resource.patch")
    def test_add_type(self, mock_patch):
        """
        Add type page should add a type to the session, not call the API
        """
        self.update_session({
            'barrier_types': [
                {
                    'id': type_id,
                    'title': "Title",
                } for type_id in self.barrier['barrier_types']
            ],
        })

        response = self.client.post(
            reverse(
                'barriers:add_type',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'barrier_type': '117'},
        )
        assert response.status_code == HTTPStatus.FOUND

        session_barrier_type_ids = [
            type['id'] for type in self.client.session['barrier_types']
        ]
        assert session_barrier_type_ids == (
            self.barrier['barrier_types'] + [117]
        )
        assert mock_patch.called is False

    def test_edit_types_confirmation_form(self):
        """
        Edit Barrier Types form should match the types in the session
        """
        self.update_session({
            'barrier_types': [
                {
                    'id': type_id,
                    'title': "Title",
                } for type_id in self.barrier['barrier_types'] + [117]
            ],
        })

        response = self.client.get(
            reverse(
                'barriers:edit_types_session',
                kwargs={'barrier_id': self.barrier['id']}
            ),
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context['form']
        assert form.initial['barrier_types'] == (
            self.barrier['barrier_types'] + [117]
        )

    @patch("utils.api_client.Resource.patch")
    def test_edit_types_confirm(self, mock_patch):
        """
        Saving barrier types should call the API
        """
        new_types = self.barrier['barrier_types'] + [117]

        self.update_session({
            'barrier_types': [
                {
                    'id': type_id,
                    'title': "Title",
                } for type_id in new_types
            ],
        })

        response = self.client.post(
            reverse(
                'barriers:edit_types_session',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'barrier_types': new_types},
        )

        mock_patch.assert_called_with(
            id=self.barrier['id'],
            barrier_types=[str(barrier_type) for barrier_type in new_types],
        )
        assert response.status_code == HTTPStatus.FOUND

    @patch("utils.api_client.Resource.patch")
    def test_remove_type(self, mock_patch):
        """
        Removing a type should remove it from the session, not call the API
        """
        new_types = self.barrier['barrier_types'] + [117]

        self.update_session({
            'barrier_types': [
                {
                    'id': type_id,
                    'title': "Title",
                } for type_id in new_types
            ],
        })

        response = self.client.post(
            reverse(
                'barriers:remove_type',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'barrier_type_id': self.barrier['barrier_types'][0]},
        )
        assert response.status_code == HTTPStatus.FOUND

        session_barrier_type_ids = [
            type['id'] for type in self.client.session['barrier_types']
        ]
        assert session_barrier_type_ids == (
            self.barrier['barrier_types'][1:] + [117]
        )
        assert mock_patch.called is False
