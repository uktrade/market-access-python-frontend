from http import HTTPStatus

from django.urls import reverse
from mock import patch

from core.tests import MarketAccessTestCase


class EditBarrierExportTypesTestCase(MarketAccessTestCase):
    new_export_type = ["goods"]
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
            each["name"] for each in self.barrier["export_types"]
        ]
        assert form.initial["export_description"] == self.barrier["export_description"]

    @patch("utils.api.resources.APIResource.patch")
    def test_add_export_type(self, mock_patch):
        """
        Saving export_types should call the API
        """
        response = self.client.post(
            reverse(
                "barriers:edit_export_types",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "export_types": self.new_export_type,
                "export_description": self.barrier["export_description"]
            },
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"], export_types=self.new_export_type
        )
        assert response.status_code == HTTPStatus.FOUND

    @patch("utils.api.resources.APIResource.patch")
    def test_update_export_description(self, mock_patch):
        """
        Saving export_descriptions should call the API
        """
        new_description = "new description"
        response = self.client.post(
            reverse(
                "barriers:edit_export_types",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "export_types": self.new_export_type,
                "export_description": new_description
            },
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"], export_description=new_description
        )
        assert response.status_code == HTTPStatus.FOUND
