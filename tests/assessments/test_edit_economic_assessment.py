from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

import mock
from mock import patch


class EditEconomicAssessmentTestCase(MarketAccessTestCase):
    def setUp(self):
        self.barrier['has_assessment'] = True
        super().setUp()

    def tearDown(self):
        self.barrier['has_assessment'] = False

    @patch("utils.api.resources.BarriersResource.get_assessment")
    def test_initial_data(self, mock_get_assessment):
        mock_get_assessment.return_value = self.assessments[0]

        response = self.client.get(
            reverse(
                'barriers:economic_assessment',
                kwargs={'barrier_id': self.barrier['id']}
            )
        )

        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        form = response.context['form']
        assert form.initial['impact'] == self.assessments[0].impact
        assert form.initial['description'] == self.assessments[0].explanation

    @patch("utils.api.resources.BarriersResource.create_assessment")
    @patch("utils.api.resources.BarriersResource.update_assessment")
    def test_success(self, mock_update, mock_create):
        self.delete_session_key('assessment_documents')
        response = self.client.post(
            reverse(
                'barriers:economic_assessment',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={
                "impact": "HIGH",
                "description": "Test description",
            }
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_update.assert_called_with(
            barrier_id=self.barrier['id'],
            impact="HIGH",
            explanation="Test description",
            documents=[],
        )
        assert mock_create.called is False

    @patch("utils.api.resources.BarriersResource.create_assessment")
    @patch("utils.api.resources.BarriersResource.update_assessment")
    def test_success_with_ajax_document(
        self,
        mock_update,
        mock_create,
    ):
        document_id = "38ab3bed-fc19-4770-9c12-9e26667efbc5"
        self.delete_session_key('assessment_documents')
        response = self.client.post(
            reverse(
                'barriers:economic_assessment',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={
                "impact": "HIGH",
                "description": "Test description",
                "document_ids": [document_id],
            }
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_update.assert_called_with(
            barrier_id=self.barrier['id'],
            impact="HIGH",
            explanation="Test description",
            documents=[document_id],
        )
        assert mock_create.called is False

    @patch("utils.api.client.DocumentsResource.check_scan_status")
    @patch("utils.api.client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api.client.DocumentsResource.create")
    @patch("utils.api.resources.BarriersResource.update_assessment")
    def test_success_with_non_ajax_document(
        self,
        mock_update_assessment,
        mock_create_document,
        mock_upload_to_s3,
        mock_complete_upload,
        mock_check_scan_status,
    ):
        document_id = "38ab3bed-fc19-4770-9c12-9e26667efbc5"
        mock_create_document.return_value = {
            'id': document_id,
            'signed_upload_url': "someurl",
        }

        self.delete_session_key('assessment_documents')

        with open('tests/files/attachment.jpeg', 'rb') as document:
            response = self.client.post(
                reverse(
                    'barriers:economic_assessment',
                    kwargs={'barrier_id': self.barrier['id']}
                ),
                data={
                    "impact": "HIGH",
                    "description": "Test description",
                    "document": document,
                }
            )

        assert response.status_code == HTTPStatus.FOUND
        assert mock_create_document.called is True
        mock_update_assessment.assert_called_with(
            barrier_id=self.barrier['id'],
            impact="HIGH",
            explanation="Test description",
            documents=[document_id],
        )
        mock_upload_to_s3.assert_called_with(url="someurl", document=mock.ANY)
        mock_complete_upload.assert_called_with(document_id)
        mock_check_scan_status.assert_called_with(document_id)
