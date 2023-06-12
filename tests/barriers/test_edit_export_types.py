from http import HTTPStatus

from django.urls import reverse
from mock import patch

from core.tests import MarketAccessTestCase


class EditBarrierExportTypesTestCase(MarketAccessTestCase):
    new_export_type = "services"

    def test_edit_export_types_landing_page(self):
        """
        Landing page should load the barrier's export types into the session
        """
        response = self.client.get(
            reverse(
                "barriers:edit_export_types", kwargs={"barrier_id": self.barrier["id"]}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["export_types"] == [
            export_type for export_type in self.barrier["export_types"]
        ]
        assert self.client.session["export_types"] == [
            export_type for export_type in self.barrier["export_types"]
        ]

    def test_add_export_types_choices(self):
        """
        Add Sector page should not include current sectors in choices
        """
        self.update_session(
            {
                "export_types": [
                    export_type for export_type in self.barrier["export_types"]
                ],
            }
        )

        response = self.client.get(
            reverse(
                "barriers:add_export_types", kwargs={"barrier_id": self.barrier["id"]}
            ),
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]

        choice_values = [k for k, v in form.fields["export_type"].choices]
        for export_type in self.barrier["export_types"]:
            assert export_type not in choice_values

    @patch("utils.api.resources.APIResource.patch")
    def test_add_export_type(self, mock_patch):
        """
        Add Sector page should add a sector to the session, not call the API
        """
        self.update_session(
            {
                "export_types": [
                    export_type for export_type in self.barrier["export_types"]
                ],
            }
        )
        response = self.client.post(
            reverse(
                "barriers:add_export_types", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"export_type": self.new_export_type},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert self.client.session["export_types"] == (
            [export_type for export_type in self.barrier["export_types"]]
            + [self.new_export_type]
        )
        assert mock_patch.called is False

    def test_edit_export_type_confirmation_form(self):
        """
        Edit Sectors form should match the sectors in the session
        """
        self.update_session(
            {
                "export_types": [
                    export_type for export_type in self.barrier["export_types"]
                ]
            }
        )

        response = self.client.get(
            reverse(
                "barriers:edit_export_types_session",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.OK
        assert self.client.session["export_types"] == (
            [export_type for export_type in self.barrier["export_types"]]
            + [self.new_export_type]
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_export_type_confirm(self, mock_patch):
        """
        Saving sectors should call the API
        """
        new_export_types = [self.new_export_type]
        response = self.client.post(
            reverse(
                "barriers:edit_export_types_session",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"export_types": new_export_types},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"], export_types=new_export_types
        )
        assert response.status_code == HTTPStatus.FOUND

    @patch("utils.api.resources.APIResource.patch")
    def test_remove_export_type(self, mock_patch):
        """
        Removing a sector should remove it from the session, not call the API
        """
        self.update_session(
            {
                "export_types": [
                    export_type for export_type in self.barrier["export_types"]
                ]
            }
        )

        response = self.client.post(
            reverse(
                "barriers:remove_export_type", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"export_type": "goods"},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert self.client.session["export_types"] == ["investment"]
        assert mock_patch.called is False
