from http import HTTPStatus

from django.conf import settings
from django.urls import reverse

from barriers.models import Barrier
from core.tests import MarketAccessTestCase

from utils.models import ModelList

from mock import patch


class WatchlistTestCase(MarketAccessTestCase):
    simple_watchlist = {"name": "Simple", "filters": {"priority": ["MEDIUM"]}}
    test_watchlist = {"name": "Test", "filters": {"search": "Test"}}
    complex_watchlist = {
        "name": "Complex",
        "filters": {
            "search": "Test",
            "country": ["9f5f66a0-5d95-e211-a939-e4115bead28a"],
            "sector": [
                "9538cecc-5f95-e211-a939-e4115bead28a",
                "a538cecc-5f95-e211-a939-e4115bead28a",
            ],
            "type": ["123"],
            "region": ["3e6809d6-89f6-4590-8458-1d0dab73ad1a"],
            "priority": ["HIGH", "MEDIUM"],
            "status": ["1", "2", "3"],
            "user": "1",
        },
    }
    old_watchlist = {
        "name": "Node",
        "filters": {"search": ["old watchlist test"], "createdBy": ["1"],},
    }

    def set_watchlists(self, *args):
        self.update_session(
            {"user_data": {"user_profile": {"watchList": {"lists": args}}}}
        )

    def test_empty_watchlists(self):
        response = self.client.get(reverse("barriers:dashboard"))
        assert response.status_code == HTTPStatus.OK
        assert response.context["watchlists"] == []
        assert response.context["barriers"] == []
        assert response.context["can_add_watchlist"] is True

    @patch("utils.api.resources.APIResource.list")
    def test_simple_watchlist(self, mock_list):
        self.set_watchlists(self.simple_watchlist)

        response = self.client.get(reverse("barriers:dashboard"))
        assert response.status_code == HTTPStatus.OK
        assert len(response.context["watchlists"]) == 1
        assert response.context["watchlists"][0].name == "Simple"
        mock_list.assert_called_with(
            priority="MEDIUM",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            ordering="-modified_on",
        )

    @patch("utils.api.resources.APIResource.list")
    def test_complex_watchlist(self, mock_list):
        self.set_watchlists(self.complex_watchlist)
        barrier_list = ModelList(model=Barrier, data=self.barriers, total_count=2,)
        mock_list.return_value = barrier_list

        response = self.client.get(reverse("barriers:dashboard"))
        assert response.status_code == HTTPStatus.OK
        assert len(response.context["watchlists"]) == 1
        assert response.context["watchlists"][0].name == "Complex"
        assert response.context["barriers"] == barrier_list
        assert response.context["can_add_watchlist"] is True
        mock_list.assert_called_with(
            ordering="-modified_on",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            text="Test",
            location=(
                "9f5f66a0-5d95-e211-a939-e4115bead28a,"
                "3e6809d6-89f6-4590-8458-1d0dab73ad1a"
            ),
            sector=(
                "9538cecc-5f95-e211-a939-e4115bead28a,"
                "a538cecc-5f95-e211-a939-e4115bead28a"
            ),
            barrier_type="123",
            priority="HIGH,MEDIUM",
            status="1,2,3",
            user="1",
        )

    @patch("utils.api.resources.APIResource.list")
    def test_old_watchlist(self, mock_list):
        self.set_watchlists(self.old_watchlist)
        barrier_list = ModelList(model=Barrier, data=self.barriers, total_count=2,)
        mock_list.return_value = barrier_list

        response = self.client.get(reverse("barriers:dashboard"))
        assert response.status_code == HTTPStatus.OK
        assert len(response.context["watchlists"]) == 1
        assert response.context["watchlists"][0].name == "Node"
        assert response.context["barriers"] == barrier_list
        assert response.context["can_add_watchlist"] is True
        mock_list.assert_called_with(
            ordering="-modified_on",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            text="old watchlist test",
            user=1,
        )

    @patch("utils.api.resources.APIResource.list")
    def test_sort(self, mock_list):
        self.set_watchlists(self.simple_watchlist)

        response = self.client.get(
            reverse("barriers:dashboard"), data={"sort": "-status"}
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            priority="MEDIUM",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            ordering="-status",
        )

        response = self.client.get(
            reverse("barriers:dashboard"), data={"sort": "export_country"}
        )
        assert response.status_code == HTTPStatus.OK
        mock_list.assert_called_with(
            priority="MEDIUM",
            limit=settings.API_RESULTS_LIMIT,
            offset=0,
            ordering="export_country",
        )

    @patch("utils.api.resources.APIResource.list")
    def test_tabs(self, mock_list):
        self.set_watchlists(self.complex_watchlist, self.simple_watchlist)

        response = self.client.get(reverse("barriers:dashboard"), data={"list": "1"})
        assert response.status_code == HTTPStatus.OK
        assert len(response.context["watchlists"]) == 2
        assert response.context["selected_watchlist"].name == "Simple"
        assert response.context["can_add_watchlist"] is True

    @patch("utils.api.resources.APIResource.list")
    def test_can_add_watchlist(self, mock_list):
        self.set_watchlists(*[self.simple_watchlist] * 3)

        response = self.client.get(reverse("barriers:dashboard"))
        assert response.status_code == HTTPStatus.OK
        assert len(response.context["watchlists"]) == 3
        assert response.context["can_add_watchlist"] is False

    @patch("utils.api.resources.APIResource.list")
    def test_pagination(self, mock_list):
        self.set_watchlists(*[self.simple_watchlist] * 3)
        mock_list.return_value = ModelList(
            model=Barrier,
            data=[self.barrier] * settings.API_RESULTS_LIMIT,
            total_count=87,
        )

        response = self.client.get(
            reverse("barriers:dashboard"), data={"page": "7", "list": "2"},
        )

        assert response.status_code == HTTPStatus.OK

        mock_list.assert_called_with(
            priority="MEDIUM",
            ordering="-modified_on",
            limit=settings.API_RESULTS_LIMIT,
            offset=60,
        )
        barriers = response.context["barriers"]
        assert len(barriers) == settings.API_RESULTS_LIMIT
        assert barriers.total_count == 87

        pagination = response.context["pagination"]
        assert pagination["total_pages"] == 9
        assert pagination["pages"][0]["label"] == 1
        assert pagination["pages"][0]["url"] == "list=2&page=1"
        page_labels = [page["label"] for page in pagination["pages"]]
        assert page_labels == [1, "...", 6, 7, 8, 9]

    def test_rename_watchlist_initial(self):
        self.set_watchlists(self.complex_watchlist, self.simple_watchlist)
        response = self.client.get(
            reverse("barriers:rename_watchlist", kwargs={"index": 0}),
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["name"] == self.complex_watchlist["name"]

    @patch("utils.api.resources.UsersResource.patch")
    def test_rename_watchlist_error(self, mock_patch):
        self.set_watchlists(self.complex_watchlist, self.simple_watchlist)
        response = self.client.post(
            reverse("barriers:rename_watchlist", kwargs={"index": 0}), data={"name": ""}
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "name" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.UsersResource.patch")
    def test_rename_watchlist_success(self, mock_patch):
        self.set_watchlists(self.simple_watchlist, self.test_watchlist)
        response = self.client.post(
            reverse("barriers:rename_watchlist", kwargs={"index": 1}),
            data={"name": "New Name"},
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            user_profile={
                "watchList": {
                    "lists": [
                        self.simple_watchlist,
                        {"name": "New Name", "filters": {"search": "Test"}},
                    ]
                }
            }
        )

    @patch("utils.api.resources.UsersResource.patch")
    def test_remove_watchlist_invalid(self, mock_patch):
        self.set_watchlists(self.simple_watchlist, self.test_watchlist)
        assert len(self.client.session.get_watchlists()) == 2
        response = self.client.get(
            reverse("barriers:remove_watchlist", kwargs={"index": 5}),
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.called is False
        assert len(self.client.session.get_watchlists()) == 2

    @patch("utils.api.resources.UsersResource.patch")
    def test_remove_watchlist_success(self, mock_patch):
        self.set_watchlists(self.simple_watchlist, self.test_watchlist)
        assert len(self.client.session.get_watchlists()) == 2
        response = self.client.get(
            reverse("barriers:remove_watchlist", kwargs={"index": 0}),
        )
        assert response.status_code == HTTPStatus.FOUND
        mock_patch.assert_called_with(
            user_profile={"watchList": {"lists": [self.test_watchlist]}}
        )
        assert len(self.client.session.get_watchlists()) == 1

    @patch("utils.api.resources.APIResource.list")
    def test_edit_watchlist_have_filters_changed(self, mock_list):
        self.set_watchlists(self.simple_watchlist, self.test_watchlist)
        response = self.client.get(
            reverse("barriers:find_a_barrier"), data={"search": "Test", "edit": 1},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.context["have_filters_changed"] is False

        response = self.client.get(
            reverse("barriers:find_a_barrier"),
            data={"search": "Test", "priority": ["HIGH"], "edit": 1},
        )
        assert response.status_code == HTTPStatus.OK
        assert response.context["have_filters_changed"] is True

    @patch("utils.api.resources.APIResource.list")
    def test_edit_watchlist_initial(self, mock_list):
        self.set_watchlists(self.simple_watchlist, self.test_watchlist)
        response = self.client.get(
            reverse("barriers:edit_watchlist"),
            data={"search": "Test", "priority": ["HIGH"], "edit": 1},
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["name"] == self.test_watchlist["name"]

    @patch("utils.api.resources.UsersResource.patch")
    @patch("utils.api.resources.APIResource.list")
    def test_edit_watchlist_error(self, mock_list, mock_patch):
        self.set_watchlists(self.simple_watchlist, self.test_watchlist)
        response = self.client.post(
            f"{reverse('barriers:edit_watchlist')}" "?search=Test&priority=HIGH&edit=1",
            data={"name": ""},
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "name" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.UsersResource.patch")
    @patch("utils.api.resources.APIResource.list")
    def test_edit_watchlist_success(self, mock_list, mock_patch):
        self.set_watchlists(self.simple_watchlist, self.test_watchlist)
        response = self.client.post(
            f"{reverse('barriers:edit_watchlist')}" "?search=Test&priority=HIGH&edit=1",
            data={"name": "Edited Watchlist"},
        )
        assert response.status_code == HTTPStatus.FOUND

        mock_patch.assert_called_with(
            user_profile={
                "watchList": {
                    "lists": [
                        self.simple_watchlist,
                        {
                            "name": "Edited Watchlist",
                            "filters": {"search": "Test", "priority": ["HIGH"]},
                        },
                    ]
                }
            }
        )
        assert len(self.client.session.get_watchlists()) == 2

    @patch("utils.api.resources.UsersResource.patch")
    @patch("utils.api.resources.APIResource.list")
    def test_save_watchlist_no_name(self, mock_list, mock_patch):
        self.set_watchlists(self.simple_watchlist, self.test_watchlist)
        assert len(self.client.session.get_watchlists()) == 2

        response = self.client.post(
            f"{reverse('barriers:save_watchlist')}"
            "?search=Test&priority=HIGH&status=2",
            data={"name": "", "replace_or_new": "new"},
        )

        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "name" in form.errors
        assert "replace_or_new" not in form.errors
        assert "replace_index" not in form.errors
        assert mock_patch.called is False
        assert len(self.client.session.get_watchlists()) == 2

    @patch("utils.api.resources.UsersResource.patch")
    @patch("utils.api.resources.APIResource.list")
    def test_save_watchlist_no_replace_or_new(self, mock_list, mock_patch):
        self.set_watchlists(self.simple_watchlist, self.test_watchlist)
        assert len(self.client.session.get_watchlists()) == 2

        response = self.client.post(
            f"{reverse('barriers:save_watchlist')}"
            "?search=Test&priority=HIGH&status=2",
            data={"name": "Saved Watchlist"},
        )

        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "replace_or_new" in form.errors
        assert "replace_index" not in form.errors
        assert mock_patch.called is False
        assert len(self.client.session.get_watchlists()) == 2

    @patch("utils.api.resources.UsersResource.patch")
    @patch("utils.api.resources.APIResource.list")
    def test_save_watchlist_no_replace_index(self, mock_list, mock_patch):
        self.set_watchlists(self.simple_watchlist, self.test_watchlist)
        assert len(self.client.session.get_watchlists()) == 2

        response = self.client.post(
            f"{reverse('barriers:save_watchlist')}"
            "?search=Test&priority=HIGH&status=2",
            data={"name": "Saved Watchlist", "replace_or_new": "replace"},
        )

        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.is_valid() is False
        assert "replace_or_new" not in form.errors
        assert "replace_index" in form.errors
        assert mock_patch.called is False
        assert len(self.client.session.get_watchlists()) == 2

    @patch("utils.api.resources.UsersResource.patch")
    @patch("utils.api.resources.APIResource.list")
    def test_new_watchlist_success(self, mock_list, mock_patch):
        self.set_watchlists(self.simple_watchlist, self.test_watchlist)
        assert len(self.client.session.get_watchlists()) == 2

        response = self.client.post(
            f"{reverse('barriers:save_watchlist')}"
            "?search=Test&priority=HIGH&status=2",
            data={"name": "New Watchlist", "replace_or_new": "new"},
        )

        assert response.status_code == HTTPStatus.FOUND

        mock_patch.assert_called_with(
            user_profile={
                "watchList": {
                    "lists": [
                        self.simple_watchlist,
                        self.test_watchlist,
                        {
                            "name": "New Watchlist",
                            "filters": {
                                "search": "Test",
                                "priority": ["HIGH"],
                                "status": ["2"],
                            },
                        },
                    ]
                }
            }
        )
        assert len(self.client.session.get_watchlists()) == 3

    @patch("utils.api.resources.UsersResource.patch")
    @patch("utils.api.resources.APIResource.list")
    def test_replace_watchlist_success(self, mock_list, mock_patch):
        self.set_watchlists(self.simple_watchlist, self.test_watchlist)
        assert len(self.client.session.get_watchlists()) == 2

        response = self.client.post(
            f"{reverse('barriers:save_watchlist')}"
            "?search=Test&priority=HIGH&status=2",
            data={
                "name": "Replaced Watchlist",
                "replace_or_new": "replace",
                "replace_index": "0",
            },
        )

        assert response.status_code == HTTPStatus.FOUND

        mock_patch.assert_called_with(
            user_profile={
                "watchList": {
                    "lists": [
                        {
                            "name": "Replaced Watchlist",
                            "filters": {
                                "search": "Test",
                                "priority": ["HIGH"],
                                "status": ["2"],
                            },
                        },
                        self.test_watchlist,
                    ]
                }
            }
        )
        assert len(self.client.session.get_watchlists()) == 2
