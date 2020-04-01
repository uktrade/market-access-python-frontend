from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from utils.exceptions import FileUploadError

import mock
from mock import patch


class NotesTestCase(MarketAccessTestCase):
    def test_edit_note_initial_data(self):
        response = self.client.get(
            reverse(
                "barriers:edit_note",
                kwargs={"barrier_id": self.barrier["id"], "note_id": "1"},
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        assert response.context["form"].initial == {"note": self.notes[0].text}
        assert response.context["documents"][0]["id"] == (self.notes[0].documents[0].id)

    @patch("utils.api.client.NotesResource.create")
    def test_note_cannot_be_empty(self, mock_create):
        response = self.client.post(
            reverse(
                "barriers:edit_note",
                kwargs={"barrier_id": self.barrier["id"], "note_id": "1"},
            ),
            data={"note": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "note" in form.errors
        assert mock_create.called is False

    @patch("utils.api.client.NotesResource.update")
    def test_edit_note_success(self, mock_update_note):
        response = self.client.post(
            reverse(
                "barriers:edit_note",
                kwargs={"barrier_id": self.barrier["id"], "note_id": "1"},
            ),
            data={"note": "Edited note"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_update_note.assert_called_with(
            id=1, text="Edited note", documents=[],
        )

    @patch("utils.api.client.NotesResource.update")
    def test_edit_note_success_with_ajax_document(self, mock_update_note):
        document_id = "38ab3bed-fc19-4770-9c12-9e26667efbc5"
        response = self.client.post(
            reverse(
                "barriers:edit_note",
                kwargs={"barrier_id": self.barrier["id"], "note_id": "1"},
            ),
            data={"note": "Edited note", "document_ids": [document_id]},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_update_note.assert_called_with(
            id=1, text="Edited note", documents=[document_id],
        )

    @patch("utils.api.client.DocumentsResource.check_scan_status")
    @patch("utils.api.client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api.client.DocumentsResource.create")
    @patch("utils.api.client.NotesResource.update")
    def test_edit_note_success_with_non_ajax_document(
        self,
        mock_update_note,
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
                    "barriers:edit_note",
                    kwargs={"barrier_id": self.barrier["id"], "note_id": "1"},
                ),
                data={"note": "New note", "document": document},
            )

        assert response.status_code == HTTPStatus.FOUND
        assert mock_create_document.called is True
        mock_update_note.assert_called_with(
            id=1, text="New note", documents=[document_id],
        )
        mock_upload_to_s3.assert_called_with(url="someurl", document=mock.ANY)
        mock_complete_upload.assert_called_with(document_id)
        mock_check_scan_status.assert_called_with(document_id)

    @patch("utils.api.client.DocumentsResource.check_scan_status")
    @patch("utils.api.client.DocumentsResource.complete_upload")
    @patch("barriers.forms.mixins.DocumentMixin.upload_to_s3")
    @patch("utils.api.client.DocumentsResource.create")
    @patch("utils.api.client.NotesResource.update")
    def test_edit_note_with_document_non_ajax_scan_fail(
        self,
        mock_update_note,
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

        with open("tests/files/attachment.jpeg", "rb") as document:
            response = self.client.post(
                reverse(
                    "barriers:edit_note",
                    kwargs={"barrier_id": self.barrier["id"], "note_id": "1"},
                ),
                data={"note": "New note", "document": document},
            )

        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "document" in form.errors
        assert mock_create_document.called is True
        assert mock_upload_to_s3.called is True
        assert mock_complete_upload.called is True
        assert mock_check_scan_status.called is True
        assert mock_update_note.called is False

    @patch("utils.api.client.NotesResource.delete")
    def test_delete_note_confirmation_ajax(self, mock_delete_note):
        response = self.client.get(
            reverse(
                "barriers:delete_note",
                kwargs={"barrier_id": self.barrier["id"], "note_id": 1},
            ),
            xhr=True,
        )
        assert response.status_code == HTTPStatus.OK
        mock_delete_note.called is False
        assert "note" in response.context

    @patch("utils.api.client.NotesResource.delete")
    def test_delete_note_confirmation_non_ajax(self, mock_delete_note):
        response = self.client.get(
            reverse(
                "barriers:delete_note",
                kwargs={"barrier_id": self.barrier["id"], "note_id": 1},
            ),
        )
        assert response.status_code == HTTPStatus.OK
        mock_delete_note.called is False
        assert "note" in response.context

    @patch("utils.api.client.NotesResource.delete")
    def test_delete_note_success(self, mock_delete_note):
        response = self.client.post(
            reverse(
                "barriers:delete_note",
                kwargs={"barrier_id": self.barrier["id"], "note_id": 1},
            ),
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_delete_note.assert_called_with(1)
