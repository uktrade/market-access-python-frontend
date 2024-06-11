from http import HTTPStatus

import mock
from django.conf import settings
from django.urls import reverse
from mock import patch

from core.tests import MarketAccessTestCase
from utils.exceptions import FileUploadError, ScanError


class EconomicAssessmentDocumentsTestCase(MarketAccessTestCase):
    @patch("utils.api.client.DocumentsResource.check_scan_status")
    @patch("utils.api.client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api.client.DocumentsResource.create")
    def test_add_economic_assessment_document_ajax(
        self,
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

        with open("tests/files/attachment.jpeg", "rb") as document:
            response = self.client.post(
                reverse(
                    "barriers:add_economic_assessment_document",
                    kwargs={"barrier_id": self.barrier["id"]},
                ),
                data={"document": document},
                xhr=True,
            )

        assert response.status_code == HTTPStatus.OK
        response_data = response.json()
        assert response_data["documentId"] == document_id
        assert "delete_url" in response_data
        assert response_data["file"]["name"] == "attachment.jpeg"

        session_key = f"barrier:{self.barrier['id']}:economic_assessments:new:documents"
        assert self.client.session[session_key][0]["id"] == document_id
        assert mock_create_document.called is True
        mock_upload_to_s3.assert_called_with(url="someurl", document=mock.ANY)
        mock_complete_upload.assert_called_with(document_id)
        mock_check_scan_status.assert_called_with(document_id)

    @patch("utils.api.client.DocumentsResource.check_scan_status")
    @patch("utils.api.client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api.client.DocumentsResource.create")
    def test_add_economic_assessment_document_ajax_scan_fail(
        self,
        mock_create_document,
        mock_upload_to_s3,
        mock_complete_upload,
        mock_check_scan_status,
    ):
        mock_check_scan_status.side_effect = ScanError("Scan failed")

        with open("tests/files/attachment.jpeg", "rb") as document:
            response = self.client.post(
                reverse(
                    "barriers:add_economic_assessment_document",
                    kwargs={"barrier_id": self.barrier["id"]},
                ),
                data={"document": document},
                xhr=True,
            )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        response_data = response.json()
        assert response_data["message"] == "Scan failed"

    @patch("utils.api.client.DocumentsResource.check_scan_status")
    @patch("utils.api.client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api.client.DocumentsResource.create")
    def test_add_economic_assessment_document_ajax_upload_fail(
        self,
        mock_create_document,
        mock_upload_to_s3,
        mock_complete_upload,
        mock_check_scan_status,
    ):
        mock_check_scan_status.side_effect = FileUploadError("Upload failed")

        with open("tests/files/attachment.jpeg", "rb") as document:
            response = self.client.post(
                reverse(
                    "barriers:add_economic_assessment_document",
                    kwargs={"barrier_id": self.barrier["id"]},
                ),
                data={"document": document},
                xhr=True,
            )

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        response_data = response.json()
        assert response_data["message"] == "Upload failed"

    def test_cancel_new_economic_assessment_document_ajax(self):
        session_key = f"barrier:{self.barrier['id']}:economic_assessments:new:documents"
        self.update_session({session_key: [{"id": "1"}]})

        assert session_key in self.client.session

        self.client.post(
            reverse(
                "barriers:cancel_economic_assessment_document",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            xhr=True,
        )

        assert session_key not in self.client.session

    def test_cancel_edit_economic_assessment_document_ajax(self):
        session_key = f"barrier:{self.barrier['id']}:economic_assessments:new:documents"
        self.update_session({session_key: [{"id": "1"}]})

        assert session_key in self.client.session

        self.client.get(
            reverse(
                "barriers:cancel_economic_assessment_document",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"assessment_id": "1"},
            xhr=True,
        )

        assert session_key not in self.client.session

    def test_delete_new_economic_assessment_document_ajax(self):
        document_ids = [
            "309d9ef4-4379-4514-ae5f-3399ba7f2ca6",
            "edc71297-93e4-42b1-9d7a-122fbb18a092",
        ]
        session_key = f"barrier:{self.barrier['id']}:economic_assessments:new:documents"
        self.update_session(
            {
                session_key: [
                    {"id": document_ids[0]},
                    {"id": document_ids[1]},
                ]
            }
        )
        self.client.post(
            reverse(
                "barriers:delete_economic_assessment_document",
                kwargs={
                    "barrier_id": self.barrier["id"],
                    "document_id": document_ids[0],
                },
            ),
            xhr=True,
        )
        session_document_ids = [
            document["id"] for document in self.client.session[session_key]
        ]
        assert session_document_ids == document_ids[1:]

    def test_strategic_assessments(self):
        url = reverse(
            "barriers:assessment_detail",
            kwargs={
                "barrier_id": self.barrier["id"],
            },
        )

        res = self.client.get(url)
        # Default to false, hidden by default
        assert settings.PRIORITISATION_STRATEGIC_ASSESSMENTS is False
        assert res.status_code == HTTPStatus.OK
        assert "assessment-item visually-hidden" in res.content.decode("utf8")

        with self.settings(PRIORITISATION_STRATEGIC_ASSESSMENTS=True):
            res = self.client.get(url)
            assert settings.PRIORITISATION_STRATEGIC_ASSESSMENTS is True
            assert res.status_code == HTTPStatus.OK
            assert "assessment-item visually-hidden" not in res.content.decode("utf8")

    def test_delete_edit_economic_assessment_document_ajax(self):
        document_ids = [
            "309d9ef4-4379-4514-ae5f-3399ba7f2ca6",
            "edc71297-93e4-42b1-9d7a-122fbb18a092",
        ]
        session_key = f"barrier:{self.barrier['id']}:economic_assessments:new:documents"
        self.update_session(
            {
                session_key: [
                    {"id": document_ids[0]},
                    {"id": document_ids[1]},
                ]
            }
        )
        url = reverse(
            "barriers:delete_economic_assessment_document",
            kwargs={
                "barrier_id": self.barrier["id"],
                "document_id": document_ids[0],
            },
        )
        self.client.post(url, xhr=True)
        session_document_ids = [
            document["id"] for document in self.client.session[session_key]
        ]
        assert session_document_ids == document_ids[1:]

    def test_delete_edit_economic_assessment_document_non_ajax(self):
        document_ids = [
            "309d9ef4-4379-4514-ae5f-3399ba7f2ca6",
            "edc71297-93e4-42b1-9d7a-122fbb18a092",
        ]
        session_key = f"barrier:{self.barrier['id']}:economic_assessments:new:documents"
        self.update_session(
            {
                session_key: [
                    {"id": document_ids[0]},
                    {"id": document_ids[1]},
                ]
            }
        )
        url = reverse(
            "barriers:delete_economic_assessment_document",
            kwargs={
                "barrier_id": self.barrier["id"],
                "document_id": document_ids[0],
            },
        )
        self.client.get(url)
        session_document_ids = [
            document["id"] for document in self.client.session[session_key]
        ]
        assert session_document_ids == document_ids[1:]
