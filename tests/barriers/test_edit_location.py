from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase
from utils.metadata import get_metadata

from mock import patch


class EditLocationTestCase(MarketAccessTestCase):
    new_country_id = "62af72a6-5d95-e211-a939-e4115bead28a"
    new_admin_area_ids = [
        "91d8b71c-430d-4e4a-afd0-7147578f41d9",
        "a5a2d421-5274-49ca-9c33-ea3282f5c618",
    ]

    def test_location_landing_page(self):
        """
        Landing page should load the barrier's location into the session
        """
        response = self.client.get(
            reverse(
                "barriers:edit_location",
                kwargs={"barrier_id": self.barrier["id"]},
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["country"] == self.barrier["export_country"]
        assert (
            form.initial["admin_areas"] == self.barrier["country_admin_areas"]
        )
        location = self.client.session["location"]
        assert location["country"] == self.barrier["export_country"]
        assert location["admin_areas"] == self.barrier["country_admin_areas"]

    def test_edit_country_choices(self):
        """
        Check the edit country page lists all countries in choices
        """
        self.update_session({
            'location': {
                'country': self.barrier['export_country'],
                'admin_areas':  self.barrier['country_admin_areas'],
            }
        })

        response = self.client.get(
            reverse(
                "barriers:edit_country",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]

        metadata = get_metadata()
        country_list = metadata.get_country_list()
        assert len(form.fields["country"].choices) == len(country_list)

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_country(self, mock_patch):
        """
        Edit country should change the country in the session, not call the API
        """
        self.update_session({
            'location': {
                'country': self.barrier['export_country'],
                'admin_areas':  self.barrier['country_admin_areas'],
            }
        })

        response = self.client.post(
            reverse(
                "barriers:edit_country",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"country": self.new_country_id},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert (
            self.client.session['location']['country'] == self.new_country_id
        )
        assert self.client.session["location"]["admin_areas"] == []
        assert mock_patch.called is False

    def test_add_admin_area_choices(self):
        """
        Check the add admin area page lists only admin areas in the country
        """
        self.update_session({
            'location': {
                'country': self.new_country_id,
                'admin_areas':  [],
            }
        })

        response = self.client.get(
            reverse(
                "barriers:add_admin_area",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]

        metadata = get_metadata()
        admin_areas = metadata.get_admin_areas_by_country(self.new_country_id)
        assert len(form.fields["admin_area"].choices) == len(admin_areas)

    @patch("utils.api.resources.APIResource.patch")
    def test_add_admin_area(self, mock_patch):
        """
        Add admin area should change the session, not call the API
        """
        self.update_session({
            'location': {
                'country': self.new_country_id,
                'admin_areas': [],
            }
        })

        response = self.client.post(
            reverse(
                "barriers:add_admin_area",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"admin_area": self.new_admin_area_ids[0]},
        )
        assert response.status_code == HTTPStatus.FOUND
        location = self.client.session["location"]
        assert location["country"] == self.new_country_id
        assert location["admin_areas"] == [self.new_admin_area_ids[0]]
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_remove_admin_area(self, mock_patch):
        """
        Removing admin area should remove it from the session, not call the API
        """
        self.update_session({
            'location': {
                'country': self.new_country_id,
                'admin_areas':  self.new_admin_area_ids,
            }
        })

        response = self.client.post(
            reverse(
                "barriers:remove_admin_area",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"admin_area": self.new_admin_area_ids[0]},
        )
        assert response.status_code == HTTPStatus.FOUND
        location = self.client.session["location"]
        assert location["country"] == self.new_country_id
        assert location["admin_areas"] == [self.new_admin_area_ids[1]]
        assert mock_patch.called is False

    def test_edit_location_confirmation_form(self):
        """
        Edit location form should match the location in the session
        """
        self.update_session({
            'location': {
                'country': self.new_country_id,
                'admin_areas':  self.new_admin_area_ids,
            }
        })

        response = self.client.get(
            reverse(
                "barriers:edit_location_session",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.initial["country"] == self.new_country_id
        assert form.initial["admin_areas"] == self.new_admin_area_ids

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_location_confirm(self, mock_patch):
        """
        Saving location should call the API
        """
        self.update_session({
            'location': {
                'country': self.new_country_id,
                'admin_areas':  self.new_admin_area_ids,
            }
        })
        response = self.client.post(
            reverse(
                "barriers:edit_location_session",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "country": self.new_country_id,
                "admin_areas": self.new_admin_area_ids,
            },
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            export_country=self.new_country_id,
            country_admin_areas=self.new_admin_area_ids,
        )
        assert response.status_code == HTTPStatus.FOUND
