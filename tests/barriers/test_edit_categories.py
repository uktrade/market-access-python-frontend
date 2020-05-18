from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from mock import patch


class EditCategoriesTestCase(MarketAccessTestCase):
    def test_edit_categories_landing_page(self):
        """
        Landing page should load the barrier's categories into the session
        """
        response = self.client.get(
            reverse("barriers:edit_categories", kwargs={"barrier_id": self.barrier["id"]})
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["categories"] == self.barrier["categories"]

        session_category_ids = [
            category["id"] for category in self.client.session["categories"]
        ]
        assert session_category_ids == self.barrier["categories"]

    def test_add_category_choices(self):
        """
        Add category page should not include current categories in choices
        """
        self.update_session(
            {
                "categories": [
                    {"id": category_id, "title": "Title",}
                    for category_id in self.barrier["categories"]
                ],
            }
        )

        response = self.client.get(
            reverse("barriers:add_category", kwargs={"barrier_id": self.barrier["id"]}),
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        choice_values = [k for k, v in form.fields["category"].choices]

        for category_id in self.barrier["categories"]:
            assert category_id not in choice_values

    @patch("utils.api.resources.APIResource.patch")
    def test_add_category(self, mock_patch):
        """
        Add category page should add a category to the session, not call the API
        """
        self.update_session(
            {
                "categories": [
                    {"id": category_id, "title": "Title",}
                    for category_id in self.barrier["categories"]
                ],
            }
        )

        response = self.client.post(
            reverse("barriers:add_category", kwargs={"barrier_id": self.barrier["id"]}),
            data={"category": "117"},
        )
        assert response.status_code == HTTPStatus.FOUND

        session_category_ids = [
            category["id"] for category in self.client.session["categories"]
        ]
        assert session_category_ids == (self.barrier["categories"] + [117])
        assert mock_patch.called is False

    def test_edit_categories_confirmation_form(self):
        """
        Edit categories form should match the categories in the session
        """
        self.update_session(
            {
                "categories": [
                    {"id": category_id, "title": "Title",}
                    for category_id in self.barrier["categories"] + [117]
                ],
            }
        )

        response = self.client.get(
            reverse(
                "barriers:edit_categories_session", kwargs={"barrier_id": self.barrier["id"]}
            ),
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.initial["categories"] == (self.barrier["categories"] + [117])

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_categories_confirm(self, mock_patch):
        """
        Saving barrier categories should call the API
        """
        new_categories = self.barrier["categories"] + [117]

        self.update_session(
            {
                "categories": [
                    {"id": category_id, "title": "Title",} for category_id in new_categories
                ],
            }
        )

        response = self.client.post(
            reverse(
                "barriers:edit_categories_session", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"categories": new_categories},
        )

        mock_patch.assert_called_with(
            id=self.barrier["id"],
            categories=[str(category) for category in new_categories],
        )
        assert response.status_code == HTTPStatus.FOUND

    @patch("utils.api.resources.APIResource.patch")
    def test_remove_category(self, mock_patch):
        """
        Removing a category should remove it from the session, not call the API
        """
        new_categories = self.barrier["categories"] + [117]

        self.update_session(
            {
                "categories": [
                    {"id": category_id, "title": "Title",} for category_id in new_categories
                ],
            }
        )

        response = self.client.post(
            reverse("barriers:remove_category", kwargs={"barrier_id": self.barrier["id"]}),
            data={"category_id": self.barrier["categories"][0]},
        )
        assert response.status_code == HTTPStatus.FOUND

        session_category_ids = [
            category["id"] for category in self.client.session["categories"]
        ]
        assert session_category_ids == (self.barrier["categories"][1:] + [117])
        assert mock_patch.called is False
