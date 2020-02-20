from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from mock import patch


class EditBarrierSectorsTestCase(MarketAccessTestCase):
    new_sector_id = "9538cecc-5f95-e211-a939-e4115bead28a"

    def test_edit_sectors_landing_page(self):
        """
        Landing page should load the barrier's sectors into the session
        """
        response = self.client.get(
            reverse("barriers:edit_sectors", kwargs={"barrier_id": self.barrier["id"]})
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["sectors"] == self.barrier["sectors"]
        assert form.initial["all_sectors"] is False
        assert self.client.session["sectors"] == self.barrier["sectors"]
        assert self.client.session["all_sectors"] is False

    def test_add_sector_choices(self):
        """
        Add Sector page should not include current sectors in choices
        """
        self.update_session(
            {"sectors": self.barrier["sectors"], "all_sectors": False,}
        )

        response = self.client.get(
            reverse("barriers:add_sectors", kwargs={"barrier_id": self.barrier["id"]}),
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]

        choice_values = [k for k, v in form.fields["sector"].choices]
        for sector_id in self.barrier["sectors"]:
            assert sector_id not in choice_values

    @patch("utils.api.resources.APIResource.patch")
    def test_add_sector(self, mock_patch):
        """
        Add Sector page should add a sector to the session, not call the API
        """
        self.update_session(
            {"sectors": self.barrier["sectors"], "all_sectors": False,}
        )

        response = self.client.post(
            reverse("barriers:add_sectors", kwargs={"barrier_id": self.barrier["id"]}),
            data={"sector": self.new_sector_id},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert self.client.session["sectors"] == (
            self.barrier["sectors"] + [self.new_sector_id]
        )
        assert self.client.session["all_sectors"] is False
        assert mock_patch.called is False

    def test_edit_sectors_confirmation_form(self):
        """
        Edit Sectors form should match the sectors in the session
        """
        self.update_session(
            {
                "sectors": self.barrier["sectors"] + [self.new_sector_id],
                "all_sectors": False,
            }
        )

        response = self.client.get(
            reverse(
                "barriers:edit_sectors_session",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.initial["sectors"] == (
            self.barrier["sectors"] + [self.new_sector_id]
        )
        assert form.initial["all_sectors"] is False

    def test_edit_sectors_confirmation_form_all_sectors(self):
        """
        Edit Sectors form should match the sectors in the session
        """
        self.update_session(
            {"sectors": [], "all_sectors": True,}
        )

        response = self.client.get(
            reverse(
                "barriers:edit_sectors_session",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.initial["sectors"] == []
        assert form.initial["all_sectors"] is True

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_sectors_confirm(self, mock_patch):
        """
        Saving sectors should call the API
        """
        new_sectors = self.barrier["sectors"] + [self.new_sector_id]
        response = self.client.post(
            reverse(
                "barriers:edit_sectors_session",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"sectors": new_sectors},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            sectors=new_sectors,
            all_sectors=False,
            sectors_affected=True,
        )
        assert response.status_code == HTTPStatus.FOUND

    @patch("utils.api.resources.APIResource.patch")
    def test_remove_sector(self, mock_patch):
        """
        Removing a sector should remove it from the session, not call the API
        """
        self.update_session(
            {
                "sectors": self.barrier["sectors"] + [self.new_sector_id],
                "all_sectors": False,
            }
        )

        response = self.client.post(
            reverse(
                "barriers:remove_sector", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"sector": self.barrier["sectors"][0]},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert self.client.session["sectors"] == [self.new_sector_id]
        assert self.client.session["all_sectors"] is False
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_add_all_sectors(self, mock_patch):
        """
        Adding all sectors should update the session, not call the API
        """
        self.update_session(
            {"sectors": self.barrier["sectors"], "all_sectors": False,}
        )

        response = self.client.get(
            reverse(
                "barriers:add_all_sectors", kwargs={"barrier_id": self.barrier["id"]}
            ),
        )
        assert response.status_code == HTTPStatus.FOUND
        assert self.client.session["sectors"] == []
        assert self.client.session["all_sectors"] is True
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_all_sectors_confirm(self, mock_patch):
        """
        Saving 'all sectors' should call the API
        """
        response = self.client.post(
            reverse(
                "barriers:edit_sectors_session",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"sectors": [], "all_sectors": True},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"], sectors=[], all_sectors=True, sectors_affected=True,
        )
        assert response.status_code == HTTPStatus.FOUND
