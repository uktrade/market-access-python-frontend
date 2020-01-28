from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from utils.exceptions import FileUploadError, ScanError

import mock
from mock import patch


class NotesTestCase(MarketAccessTestCase):
    def test_add_note_page_loads(self):
        response = self.client.get(
            reverse(
                'barriers:add_note',
                kwargs={'barrier_id': self.barrier['id']}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert 'form' in response.context
        assert response.context['form'].initial == {}

    @patch("utils.api_client.NotesResource.create")
    def test_note_cannot_be_empty(self, mock_create):
        response = self.client.post(
            reverse(
                'barriers:add_note',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'note': ''},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context['form']
        assert form.is_valid() is False
        assert 'note' in form.errors
        assert mock_create.called is False

    @patch("utils.api_client.NotesResource.create")
    def test_add_note_success(self, mock_create):
        response = self.client.post(
            reverse(
                'barriers:add_note',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'note': 'New note'},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_create.assert_called_with(
            barrier_id=self.barrier['id'],
            text="New note",
            documents=[],
        )

    @patch("utils.api_client.NotesResource.create")
    def test_add_note_success_with_ajax_document(self, mock_create):
        document_id = "38ab3bed-fc19-4770-9c12-9e26667efbc5"
        response = self.client.post(
            reverse(
                'barriers:add_note',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            data={'note': 'New note', 'document_ids': [document_id]},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_create.assert_called_with(
            barrier_id=self.barrier['id'],
            text="New note",
            documents=[document_id],
        )

    @patch("utils.api_client.DocumentsResource.check_scan_status")
    @patch("utils.api_client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api_client.DocumentsResource.create")
    @patch("utils.api_client.NotesResource.create")
    def test_add_note_success_with_non_ajax_document(
        self,
        mock_create_note,
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

        with open('tests/files/attachment.jpeg', 'rb') as document:
            response = self.client.post(
                reverse(
                    'barriers:add_note',
                    kwargs={'barrier_id': self.barrier['id']}
                ),
                data={'note': 'New note', 'document': document},
            )

        assert response.status_code == HTTPStatus.FOUND
        assert mock_create_document.called is True
        mock_create_note.assert_called_with(
            barrier_id=self.barrier['id'],
            text="New note",
            documents=[document_id],
        )
        mock_upload_to_s3.assert_called_with(url="someurl", document=mock.ANY)
        mock_complete_upload.assert_called_with(document_id)
        mock_check_scan_status.assert_called_with(document_id)

    @patch("utils.api_client.DocumentsResource.check_scan_status")
    @patch("utils.api_client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api_client.DocumentsResource.create")
    @patch("utils.api_client.NotesResource.create")
    def test_add_note_with_document_non_ajax_scan_fail(
        self,
        mock_create_note,
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

        mock_check_scan_status.side_effect = FileUploadError("Upload failed")

        with open('tests/files/attachment.jpeg', 'rb') as document:
            response = self.client.post(
                reverse(
                    'barriers:add_note',
                    kwargs={'barrier_id': self.barrier['id']}
                ),
                data={'note': 'New note', 'document': document},
            )

        assert response.status_code == HTTPStatus.OK
        form = response.context['form']
        assert form.is_valid() is False
        assert 'document' in form.errors
        assert mock_create_document.called is True
        assert mock_upload_to_s3.called is True
        assert mock_complete_upload.called is True
        assert mock_check_scan_status.called is True
        assert mock_create_note.called is False

    @patch("utils.api_client.DocumentsResource.check_scan_status")
    @patch("utils.api_client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api_client.DocumentsResource.create")
    @patch("utils.api_client.NotesResource.create")
    def test_add_note_fail_with_non_ajax_text_document(
        self,
        mock_create_note,
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

        # Text files not allowed
        with open('tests/files/attachment.txt', 'rb') as document:
            response = self.client.post(
                reverse(
                    'barriers:add_note',
                    kwargs={'barrier_id': self.barrier['id']}
                ),
                data={'note': 'New note', 'document': document},
            )

        assert response.status_code == HTTPStatus.OK
        form = response.context['form']
        assert form.is_valid() is False
        assert 'document' in form.errors
        assert mock_create_document.called is False
        assert mock_create_note.called is False
        assert mock_upload_to_s3.called is False
        assert mock_complete_upload.called is False
        assert mock_check_scan_status.called is False

    @patch("utils.api_client.DocumentsResource.check_scan_status")
    @patch("utils.api_client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api_client.DocumentsResource.create")
    @patch("utils.api_client.NotesResource.create")
    def test_add_note_document_ajax(
        self,
        mock_create_note,
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

        with open('tests/files/attachment.jpeg', 'rb') as document:
            response = self.client.post(
                reverse(
                    'barriers:add_note_document',
                    kwargs={'barrier_id': self.barrier['id']}
                ),
                data={'document': document},
                xhr=True,
            )

        assert response.status_code == HTTPStatus.OK
        response_data = response.json()
        assert response_data['documentId'] == document_id
        assert 'delete_url' in response_data
        assert response_data['file']['name'] == "attachment.jpeg"

        session_key = f"barrier:{self.barrier['id']}:note:new:documents"
        assert self.client.session[session_key][0]['id'] == document_id

        assert mock_create_document.called is True
        assert mock_create_note.called is False
        mock_upload_to_s3.assert_called_with(url="someurl", document=mock.ANY)
        mock_complete_upload.assert_called_with(document_id)
        mock_check_scan_status.assert_called_with(document_id)

    @patch("utils.api_client.DocumentsResource.check_scan_status")
    @patch("utils.api_client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api_client.DocumentsResource.create")
    def test_add_note_document_ajax_scan_fail(
        self,
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

        mock_check_scan_status.side_effect = ScanError("Scan failed")

        with open('tests/files/attachment.jpeg', 'rb') as document:
            response = self.client.post(
                reverse(
                    'barriers:add_note_document',
                    kwargs={'barrier_id': self.barrier['id']}
                ),
                data={'document': document},
                xhr=True,
            )

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        response_data = response.json()
        assert response_data['message'] == "Scan failed"

    @patch("utils.api_client.DocumentsResource.check_scan_status")
    @patch("utils.api_client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api_client.DocumentsResource.create")
    def test_add_note_document_ajax_upload_fail(
        self,
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

        mock_check_scan_status.side_effect = FileUploadError("Upload failed")

        with open('tests/files/attachment.jpeg', 'rb') as document:
            response = self.client.post(
                reverse(
                    'barriers:add_note_document',
                    kwargs={'barrier_id': self.barrier['id']}
                ),
                data={'document': document},
                xhr=True,
            )

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        response_data = response.json()
        assert response_data['message'] == "Upload failed"

    @patch("utils.api_client.DocumentsResource.check_scan_status")
    @patch("utils.api_client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api_client.DocumentsResource.create")
    @patch("utils.api_client.NotesResource.create")
    def test_cancel_note_document_ajax(
        self,
        mock_create_note,
        mock_create_document,
        mock_upload_to_s3,
        mock_complete_upload,
        mock_check_scan_status,
    ):
        session_key = f"barrier:{self.barrier['id']}:note:new:documents"
        self.update_session({session_key: [{'id': '1'}]})

        assert session_key in self.client.session

        self.client.post(
            reverse(
                'barriers:cancel_note_document',
                kwargs={'barrier_id': self.barrier['id']}
            ),
            xhr=True,
        )

        assert session_key not in self.client.session
