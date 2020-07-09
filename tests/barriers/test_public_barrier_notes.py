from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from utils.exceptions import FileUploadError

import mock
from mock import patch


class PublicBarrierNotesTestCase(MarketAccessTestCase):
    @patch("utils.api.client.PublicBarriersResource.get")
    @patch("utils.api.client.PublicBarriersResource.get_activity")
    @patch("utils.api.client.PublicBarriersResource.get_notes")
    @patch("utils.api.client.PublicBarriersResource.create_note")
    def test_note_cannot_be_empty(self, mock_create, mock_get_notes, mock_get_activity, mock_get):
        mock_get.return_value = {}
        mock_get_notes.return_value = {
            "count": 0,
            "results": []
        }
        response = self.client.post(
            reverse("barriers:public_barrier", kwargs={"barrier_id": self.barrier["id"]}),
            data={"note": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "note" in form.errors
        assert mock_create.called is False

    @patch("utils.api.client.PublicBarriersResource.get")
    @patch("utils.api.client.PublicBarriersResource.get_activity")
    @patch("utils.api.client.PublicBarriersResource.get_notes")
    @patch("utils.api.client.PublicBarriersResource.create_note")
    def test_add_note_success(self, mock_create_note, mock_get_notes, mock_get_activity, mock_get):
        mock_get_notes.return_value = {
            "count": 1,
            "results": []
        }
        response = self.client.post(
            reverse("barriers:public_barrier", kwargs={"barrier_id": self.barrier["id"]}),
            data={"note": "New note"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_create_note.assert_called_with(id=self.barrier["id"], text="New note")

    @patch("utils.api.client.PublicBarriersResource.get")
    @patch("utils.api.client.PublicBarriersResource.get_activity")
    @patch("utils.api.client.PublicBarriersResource.get_notes")
    @patch("utils.api.client.PublicBarrierNotesResource.patch")
    def test_edit_note(self, mock_patch_note, mock_get_notes, mock_get_activity, mock_get):
        mock_get_notes.return_value = {
            "count": 1,
            "results": []
        }
        response = self.client.post(
            reverse("barriers:public_barrier", kwargs={"barrier_id": self.barrier["id"]}),
            data={"note": "New note"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch_note.assert_called_with(id=self.barrier["id"], text="New note")
