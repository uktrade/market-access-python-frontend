from http import HTTPStatus

from django.urls import reverse
from mock import patch

from core.tests import MarketAccessTestCase


class EditWTOProfileTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.APIResource.patch")
    def test_bad_raised_date(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_wto_profile", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={
                "raised_date_0": "50",
                "raised_date_1": "1",
                "raised_date_2": "2020",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "raised_date" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_empty_form_success(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_wto_profile", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            wto_profile={
                "committee_notified": "",
                "committee_notification_link": "",
                "committee_notification_document": "",
                "member_states": [],
                "committee_raised_in": "",
                "meeting_minutes": "",
                "raised_date": None,
                "case_number": "",
            },
        )

    @patch("barriers.forms.mixins.DocumentMixin.upload_document")
    @patch("utils.api.resources.APIResource.patch")
    def test_full_form_success(self, mock_patch, mock_upload_document):
        mock_upload_document.return_value = {
            "id": "a9593a3f-1640-40ba-9c92-1a1186ca6e68",
            "file": {"name": "name.jpg", "size": "5000"},
        }

        with open("tests/files/attachment.jpeg", "rb") as document:
            response = self.client.post(
                reverse(
                    "barriers:edit_wto_profile",
                    kwargs={"barrier_id": self.barrier["id"]},
                ),
                data={
                    "committee_notified": "6448e88f-bf12-481f-873d-ac1199825743",
                    "committee_notification_link": "http://www.google.com",
                    "committee_notification_document": document,
                    "member_states": [
                        "a05f66a0-5d95-e211-a939-e4115bead28a",
                        "955f66a0-5d95-e211-a939-e4115bead28a",
                    ],
                    "committee_raised_in": "0d4876ab-e125-4167-9449-9f89f843921c",
                    "meeting_minutes": "",
                    "raised_date_0": "25",
                    "raised_date_1": "1",
                    "raised_date_2": "2020",
                    "case_number": "ABCD1234",
                },
            )

        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            wto_profile={
                "committee_notified": "6448e88f-bf12-481f-873d-ac1199825743",
                "committee_notification_link": "http://www.google.com",
                "committee_notification_document": (
                    "a9593a3f-1640-40ba-9c92-1a1186ca6e68"
                ),
                "member_states": [
                    "a05f66a0-5d95-e211-a939-e4115bead28a",
                    "955f66a0-5d95-e211-a939-e4115bead28a",
                ],
                "committee_raised_in": "0d4876ab-e125-4167-9449-9f89f843921c",
                "meeting_minutes": "",
                "raised_date": "2020-01-25",
                "case_number": "ABCD1234",
            },
        )

    @patch("barriers.forms.mixins.DocumentMixin.upload_document")
    @patch("utils.api.resources.APIResource.patch")
    def test_meeting_minutes_success(self, mock_patch, mock_upload_document):
        mock_upload_document.return_value = {
            "id": "a9593a3f-1640-40ba-9c92-1a1186ca6e68",
            "file": {"name": "name.jpg", "size": "5000"},
        }

        with open("tests/files/attachment.jpeg", "rb") as document:
            response = self.client.post(
                reverse(
                    "barriers:edit_wto_profile",
                    kwargs={"barrier_id": self.barrier["id"]},
                ),
                data={
                    "meeting_minutes": document,
                    "case_number": "XYZ999",
                },
            )

        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            wto_profile={
                "committee_notified": "",
                "committee_notification_link": "",
                "committee_notification_document": "",
                "member_states": [],
                "committee_raised_in": "",
                "meeting_minutes": "a9593a3f-1640-40ba-9c92-1a1186ca6e68",
                "raised_date": None,
                "case_number": "XYZ999",
            },
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_success_with_ajax_documents(self, mock_patch):
        notification_document_id = "38ab3bed-fc19-4770-9c12-9e26667efbc5"
        minutes_document_id = "6448e88f-bf12-481f-873d-ac1199825743"

        response = self.client.post(
            reverse(
                "barriers:edit_wto_profile", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={
                "committee_notification_document_id": notification_document_id,
                "meeting_minutes_id": minutes_document_id,
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            wto_profile={
                "committee_notified": "",
                "committee_notification_link": "",
                "committee_notification_document": notification_document_id,
                "member_states": [],
                "committee_raised_in": "",
                "meeting_minutes": minutes_document_id,
                "raised_date": None,
                "case_number": "",
            },
        )

    @patch("barriers.forms.mixins.DocumentMixin.upload_document")
    def test_add_document_via_ajax(self, mock_upload_document):
        document_id = "38ab3bed-fc19-4770-9c12-9e26667efbc5"
        mock_upload_document.return_value = {
            "id": document_id,
            "file": {"name": "attachment.jpeg", "size": "5000"},
        }

        with open("tests/files/attachment.jpeg", "rb") as document:
            response = self.client.post(
                reverse(
                    "barriers:add_wto_document",
                    kwargs={"barrier_id": self.barrier["id"]},
                ),
                data={"meeting_minutes": document},
                xhr=True,
            )

        assert response.status_code == HTTPStatus.OK
        response_data = response.json()
        assert response_data["documentId"] == document_id
        assert "delete_url" in response_data
        assert response_data["file"]["name"] == "attachment.jpeg"

        session_key = f"barrier:{self.barrier['id']}:wto:meeting_minutes"
        assert self.client.session[session_key]["id"] == document_id
        assert mock_upload_document.called is True

    def test_delete_document_via_ajax(self):
        document_id = "309d9ef4-4379-4514-ae5f-3399ba7f2ca6"
        barrier_id = self.barrier["id"]
        session_key = f"barrier:{barrier_id}:wto:committee_notification_document"

        self.update_session({session_key: {"id": document_id}})
        self.client.post(
            reverse(
                "barriers:delete_wto_document",
                kwargs={"barrier_id": self.barrier["id"], "document_id": document_id},
            ),
            xhr=True,
        )
        assert self.client.session[session_key] is None

    def test_delete_document_non_ajax(self):
        document_id = "309d9ef4-4379-4514-ae5f-3399ba7f2ca6"
        barrier_id = self.barrier["id"]
        session_key = f"barrier:{barrier_id}:wto:meeting_minutes"

        self.update_session({session_key: {"id": document_id}})
        self.client.get(
            reverse(
                "barriers:delete_wto_document",
                kwargs={"barrier_id": self.barrier["id"], "document_id": document_id},
            ),
        )
        assert self.client.session[session_key] is None

    @patch("utils.api.resources.APIResource.patch")
    def test_cancel_form(self, mock_patch):
        """Cancelling the form should clear the session and not call the API"""
        barrier_id = self.barrier["id"]

        notification_document_id = "38ab3bed-fc19-4770-9c12-9e26667efbc5"
        notification_session_key = (
            f"barrier:{barrier_id}:wto:committee_notification_document"
        )
        self.update_session(
            {notification_session_key: {"id": notification_document_id}}
        )

        minutes_document_id = "6448e88f-bf12-481f-873d-ac1199825743"
        minutes_session_key = f"barrier:{barrier_id}:wto:meeting_minutes"
        self.update_session({minutes_session_key: {"id": minutes_document_id}})

        assert notification_session_key in self.client.session
        assert minutes_session_key in self.client.session

        self.client.get(
            reverse(
                "barriers:cancel_wto_documents",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )

        assert notification_session_key not in self.client.session
        assert minutes_session_key not in self.client.session
        assert mock_patch.called is False
