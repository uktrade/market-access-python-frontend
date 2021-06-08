from http import HTTPStatus

from django.urls import reverse
from unittest.mock import patch

from barriers.models import PublicBarrierNote
from core.tests import MarketAccessTestCase


class PublicBarrierNotesTestCase(MarketAccessTestCase):
    @patch("utils.api.client.PublicBarriersResource.get_activity")
    @patch("utils.api.client.PublicBarriersResource.get_notes")
    @patch("utils.api.client.PublicBarriersResource.create_note")
    def test_note_cannot_be_empty(self, mock_create, mock_get_notes, mock_get_activity):
        mock_get_notes.return_value = []
        response = self.client.post(
            reverse(
                "barriers:public_barrier_detail",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"note": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "note" in form.errors
        assert mock_create.called is False

    @patch("utils.api.client.PublicBarriersResource.get_activity")
    @patch("utils.api.client.PublicBarriersResource.get_notes")
    @patch("utils.api.client.PublicBarriersResource.create_note")
    def test_add_note_success(
        self, mock_create_note, mock_get_notes, mock_get_activity
    ):
        mock_get_notes.return_value = []
        response = self.client.post(
            reverse(
                "barriers:public_barrier_detail",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"note": "New note"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_create_note.assert_called_with(id=self.barrier["id"], text="New note")

    @patch("utils.api.client.PublicBarriersResource.get_activity")
    @patch("utils.api.client.PublicBarriersResource.get_notes")
    @patch("utils.api.client.PublicBarrierNotesResource.patch")
    def test_edit_note_success(
        self, mock_patch_note, mock_get_notes, mock_get_activity
    ):
        mock_get_notes.return_value = [
            PublicBarrierNote(
                {
                    "id": 42,
                    "text": "Existing note",
                    "created_on": "2020-01-21T15:39:34.137208Z",
                    "created_by": 1,
                }
            ),
        ]
        url = reverse(
            "barriers:public_barrier_detail", kwargs={"barrier_id": self.barrier["id"]}
        )
        url = f"{url}?edit-note=42"
        response = self.client.post(url, data={"note": "Edited note"})
        assert response.status_code == HTTPStatus.FOUND
        mock_patch_note.assert_called_with(id=42, text="Edited note")

    @patch("utils.api.client.PublicBarriersResource.get_activity")
    @patch("utils.api.client.PublicBarriersResource.get_notes")
    @patch("utils.api.client.PublicBarrierNotesResource.delete")
    def test_delete_note_success(
        self, mock_delete_note, mock_get_notes, mock_get_activity
    ):
        mock_get_notes.return_value = [
            PublicBarrierNote(
                {
                    "id": 71,
                    "text": "Note",
                    "created_on": "2020-01-21T15:39:34.137208Z",
                    "created_by": 1,
                }
            ),
        ]
        url = reverse(
            "barriers:public_barrier_detail", kwargs={"barrier_id": self.barrier["id"]}
        )
        url = f"{url}?delete-note=71"
        response = self.client.post(
            url, data={"note_id": "71", "action": "delete-note"}
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_delete_note.assert_called_with(id="71")
