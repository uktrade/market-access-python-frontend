from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from mock import patch


class ChangeStatusTestCase(MarketAccessTestCase):
    def test_existing_status_not_in_choices(self):
        response = self.client.get(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        status_choice_values = [
            choice[0] for choice in form.fields['status'].choices
        ]
        assert str(self.barrier['status']['id']) not in status_choice_values

    @patch("utils.api.client.BarriersResource.set_status")
    def test_no_status_gets_error(self, mock_set_status):
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert form.is_valid() is False
        assert 'status' in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_unknown_status_errors(self, mock_set_status):
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'status': '7'}
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert form.is_valid() is False
        assert 'status' not in form.errors
        assert 'unknown_summary' in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_unknown_status_success(self, mock_set_status):
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'status': '7', 'unknown_summary': "Test unknown summary"}
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_set_status.assert_called_with(
            barrier_id=self.barrier['id'],
            status='7',
            status_summary="Test unknown summary",
        )

    @patch("utils.api.client.BarriersResource.set_status")
    def test_open_pending_errors(self, mock_set_status):
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'status': '1'}
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert form.is_valid() is False
        assert 'status' not in form.errors
        assert 'pending_summary' in form.errors
        assert 'pending_type' in form.errors
        assert 'pending_type_other' not in form.errors
        assert len(form.errors) == 2
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_open_pending_success(self, mock_set_status):
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={
                'status': '1',
                'pending_summary': "Test pending summary",
                'pending_type': "FOR_GOVT",
            }
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_set_status.assert_called_with(
            barrier_id=self.barrier['id'],
            status='1',
            sub_status="FOR_GOVT",
            status_summary="Test pending summary",
        )

    @patch("utils.api.client.BarriersResource.set_status")
    def test_open_pending_errors_other(self, mock_set_status):
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={
                'status': '1',
                'pending_summary': "Test pending summary",
                'pending_type': "OTHER",
            }
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert form.is_valid() is False
        assert 'status' not in form.errors
        assert 'pending_summary' not in form.errors
        assert 'pending_type' not in form.errors
        assert 'pending_type_other' in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_open_pending_success_other(self, mock_set_status):
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={
                'status': '1',
                'pending_summary': "Test pending summary",
                'pending_type': "OTHER",
                'pending_type_other': "Other test",
            }
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_set_status.assert_called_with(
            barrier_id=self.barrier['id'],
            status='1',
            sub_status="OTHER",
            sub_status_other="Other test",
            status_summary="Test pending summary",
        )

    @patch("utils.api.client.BarriersResource.set_status")
    def test_open_in_progress_errors(self, mock_set_status):
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'status': '2'}
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert form.is_valid() is False
        assert 'status' not in form.errors
        assert 'reopen_summary' in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_open_in_progress_success(self, mock_set_status):
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={
                'status': '2',
                'reopen_summary': "Test reopen summary",
            }
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_set_status.assert_called_with(
            barrier_id=self.barrier['id'],
            status='2',
            status_summary="Test reopen summary",
        )

    @patch("utils.api.client.BarriersResource.set_status")
    def test_partially_resolved_errors(self, mock_set_status):
        self.barrier['status']['id'] = 1
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'status': '3'}
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert form.is_valid() is False
        assert 'status' not in form.errors
        assert 'part_resolved_summary' in form.errors
        assert 'part_resolved_date' in form.errors
        assert len(form.errors) == 2
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_partially_resolved_future_date_error(self, mock_set_status):
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={
                'status': '3',
                'part_resolved_date_0': "5",
                'part_resolved_date_1': "2050",
                'part_resolved_summary': "Part resolved summary",
            }
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert form.is_valid() is False
        assert 'status' not in form.errors
        assert 'part_resolved_summary' not in form.errors
        assert 'part_resolved_date' in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_partially_resolved_bad_date_error(self, mock_set_status):
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={
                'status': '3',
                'part_resolved_date_0': "5",
                'part_resolved_date_1': "20xx",
                'part_resolved_summary': "Part resolved summary",
            }
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert form.is_valid() is False
        assert 'status' not in form.errors
        assert 'part_resolved_summary' not in form.errors
        assert 'part_resolved_date' in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_partially_resolved_success(self, mock_set_status):
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={
                'status': '3',
                'part_resolved_date_0': "12",
                'part_resolved_date_1': "2015",
                'part_resolved_summary': "Part resolved summary",
            }
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_set_status.assert_called_with(
            barrier_id=self.barrier['id'],
            status='3',
            status_date='2015-12-01',
            status_summary="Part resolved summary",
        )

    @patch("utils.api.client.BarriersResource.set_status")
    def test_fully_resolved_errors(self, mock_set_status):
        self.barrier['status']['id'] = 1
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'status': '4'}
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert form.is_valid() is False
        assert 'status' not in form.errors
        assert 'resolved_summary' in form.errors
        assert 'resolved_date' in form.errors
        assert len(form.errors) == 2
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_fully_resolved_future_date_error(self, mock_set_status):
        self.barrier['status']['id'] = 1
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={
                'status': '4',
                'resolved_date_0': "5",
                'resolved_date_1': "2050",
                'resolved_summary': "Test resolved summary",
            }
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert form.is_valid() is False
        assert 'status' not in form.errors
        assert 'resolved_summary' not in form.errors
        assert 'resolved_date' in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_fully_resolved_bad_date_error(self, mock_set_status):
        self.barrier['status']['id'] = 1
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={
                'status': '4',
                'resolved_date_0': "5",
                'resolved_date_1': "20xx",
                'resolved_summary': "Test resolved summary",
            }
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert form.is_valid() is False
        assert 'status' not in form.errors
        assert 'resolved_summary' not in form.errors
        assert 'resolved_date' in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_fully_resolved_success(self, mock_set_status):
        self.barrier['status']['id'] = 1
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={
                'status': '4',
                'resolved_date_0': "5",
                'resolved_date_1': "2019",
                'resolved_summary': "Test resolved summary",
            }
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_set_status.assert_called_with(
            barrier_id=self.barrier['id'],
            status='4',
            status_date='2019-05-01',
            status_summary="Test resolved summary",
        )

    @patch("utils.api.client.BarriersResource.set_status")
    def test_dormant_status_errors(self, mock_set_status):
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'status': '5'}
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert form.is_valid() is False
        assert 'status' not in form.errors
        assert 'dormant_summary' in form.errors
        assert len(form.errors) == 1
        assert mock_set_status.called is False

    @patch("utils.api.client.BarriersResource.set_status")
    def test_dormant_status_success(self, mock_set_status):
        response = self.client.post(
            reverse(
                'barriers:change_status',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'status': '5', 'dormant_summary': "Test dormant summary"}
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_set_status.assert_called_with(
            barrier_id=self.barrier['id'],
            status='5',
            status_summary="Test dormant summary",
        )
