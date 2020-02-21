from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from utils.exceptions import FileUploadError

import mock
from mock import patch


class NewEconomicAssessmentTestCase(MarketAccessTestCase):
    def test_new_economic_assessment_redirects(self):
        self.update_session({"assessment_documents": [{"id": "1"}]})
        response = self.client.get(
            reverse(
                "barriers:new_economic_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.FOUND
        assert "assessment_documents" not in self.client.session

    @patch("utils.api.resources.BarriersResource.create_assessment")
    @patch("utils.api.resources.BarriersResource.update_assessment")
    def test_empty_errors(self, mock_update, mock_create):
        self.delete_session_key("assessment_documents")
        response = self.client.post(
            reverse(
                "barriers:economic_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "impact" in form.errors
        assert "description" in form.errors
        assert mock_update.called is False
        assert mock_create.called is False

    @patch("utils.api.resources.BarriersResource.create_assessment")
    @patch("utils.api.resources.BarriersResource.update_assessment")
    def test_success(self, mock_update, mock_create):
        self.delete_session_key("assessment_documents")
        response = self.client.post(
            reverse(
                "barriers:economic_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"impact": "HIGH", "description": "Test description",},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_create.assert_called_with(
            barrier_id=self.barrier["id"],
            impact="HIGH",
            explanation="Test description",
            documents=[],
        )
        assert mock_update.called is False

    @patch("utils.api.resources.BarriersResource.create_assessment")
    @patch("utils.api.resources.BarriersResource.update_assessment")
    def test_add_assessment_success_with_ajax_document(
        self, mock_update, mock_create,
    ):
        document_id = "38ab3bed-fc19-4770-9c12-9e26667efbc5"
        self.delete_session_key("assessment_documents")
        response = self.client.post(
            reverse(
                "barriers:economic_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "impact": "HIGH",
                "description": "Test description",
                "document_ids": [document_id],
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_create.assert_called_with(
            barrier_id=self.barrier["id"],
            impact="HIGH",
            explanation="Test description",
            documents=[document_id],
        )
        assert mock_update.called is False

    @patch("utils.api.client.DocumentsResource.check_scan_status")
    @patch("utils.api.client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api.client.DocumentsResource.create")
    @patch("utils.api.resources.BarriersResource.create_assessment")
    def test_add_assessment_success_with_non_ajax_document(
        self,
        mock_create_assessment,
        mock_create_document,
        mock_upload_to_s3,
        mock_complete_upload,
        mock_check_scan_status,
    ):
        document_id = "38ab3bed-fc19-4770-9c12-9e26667efbc5"
        mock_create_document.return_value = {
            "id": document_id,
            "signed_upload_url": "someurl",
        }

        self.delete_session_key("assessment_documents")

        with open("tests/files/attachment.jpeg", "rb") as document:
            response = self.client.post(
                reverse(
                    "barriers:economic_assessment",
                    kwargs={"barrier_id": self.barrier["id"]},
                ),
                data={
                    "impact": "HIGH",
                    "description": "Test description",
                    "document": document,
                },
            )

        assert response.status_code == HTTPStatus.FOUND
        assert mock_create_document.called is True
        mock_create_assessment.assert_called_with(
            barrier_id=self.barrier["id"],
            impact="HIGH",
            explanation="Test description",
            documents=[document_id],
        )
        mock_upload_to_s3.assert_called_with(url="someurl", document=mock.ANY)
        mock_complete_upload.assert_called_with(document_id)
        mock_check_scan_status.assert_called_with(document_id)

    @patch("utils.api.client.DocumentsResource.check_scan_status")
    @patch("utils.api.client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api.client.DocumentsResource.create")
    @patch("utils.api.resources.BarriersResource.create_assessment")
    def test_add_assessment_with_document_non_ajax_scan_fail(
        self,
        mock_create_assessment,
        mock_create_document,
        mock_upload_to_s3,
        mock_complete_upload,
        mock_check_scan_status,
    ):
        document_id = "38ab3bed-fc19-4770-9c12-9e26667efbc5"
        mock_create_document.return_value = {
            "id": document_id,
            "signed_upload_url": "someurl",
        }

        mock_check_scan_status.side_effect = FileUploadError("Upload failed")

        self.delete_session_key("assessment_documents")

        with open("tests/files/attachment.jpeg", "rb") as document:
            response = self.client.post(
                reverse(
                    "barriers:economic_assessment",
                    kwargs={"barrier_id": self.barrier["id"]},
                ),
                data={
                    "impact": "HIGH",
                    "description": "Test description",
                    "document": document,
                },
            )

        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "document" in form.errors
        assert mock_create_document.called is True
        assert mock_upload_to_s3.called is True
        assert mock_complete_upload.called is True
        assert mock_check_scan_status.called is True
        assert mock_create_assessment.called is False

    @patch("utils.api.client.DocumentsResource.check_scan_status")
    @patch("utils.api.client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api.client.DocumentsResource.create")
    @patch("utils.api.resources.BarriersResource.create_assessment")
    def test_add_assessment_fail_with_non_ajax_text_document(
        self,
        mock_create_assessment,
        mock_create_document,
        mock_upload_to_s3,
        mock_complete_upload,
        mock_check_scan_status,
    ):
        # Text files not allowed
        with open("tests/files/attachment.txt", "rb") as document:
            response = self.client.post(
                reverse(
                    "barriers:economic_assessment",
                    kwargs={"barrier_id": self.barrier["id"]},
                ),
                data={
                    "impact": "HIGH",
                    "description": "Test description",
                    "document": document,
                },
            )

        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "document" in form.errors
        assert mock_create_document.called is False
        assert mock_create_assessment.called is False
        assert mock_upload_to_s3.called is False
        assert mock_complete_upload.called is False
        assert mock_check_scan_status.called is False
