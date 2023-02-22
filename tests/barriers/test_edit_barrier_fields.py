import logging
from http import HTTPStatus

import dateutil.parser
from django.urls import reverse
from mock import patch

from barriers.constants import TOP_PRIORITY_BARRIER_STATUS
from core.tests import MarketAccessTestCase

logger = logging.getLogger(__name__)


class EditTitleTestCase(MarketAccessTestCase):
    def test_edit_title_has_initial_data(self):
        response = self.client.get(
            reverse("barriers:edit_title", kwargs={"barrier_id": self.barrier["id"]})
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["title"] == self.barrier["title"]

    @patch("utils.api.resources.APIResource.patch")
    def test_title_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse("barriers:edit_title", kwargs={"barrier_id": self.barrier["id"]}),
            data={"title": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "title" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_title_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse("barriers:edit_title", kwargs={"barrier_id": self.barrier["id"]}),
            data={"title": "New Title"},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            title="New Title",
        )
        assert response.status_code == HTTPStatus.FOUND


class EditSummaryTestCase(MarketAccessTestCase):
    def test_edit_summary_has_initial_data(self):
        response = self.client.get(
            reverse("barriers:edit_summary", kwargs={"barrier_id": self.barrier["id"]})
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["summary"] == self.barrier["summary"]

    @patch("utils.api.resources.APIResource.patch")
    def test_summary_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse("barriers:edit_summary", kwargs={"barrier_id": self.barrier["id"]}),
            data={"summary": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "summary" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_is_summary_sensitive_is_required(self, mock_patch):
        response = self.client.post(
            reverse("barriers:edit_summary", kwargs={"barrier_id": self.barrier["id"]}),
            data={"summary": "This is a summary"},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "is_summary_sensitive" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_summary_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse("barriers:edit_summary", kwargs={"barrier_id": self.barrier["id"]}),
            data={
                "summary": "New summary",
                "is_summary_sensitive": "yes",
            },
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            summary="New summary",
            is_summary_sensitive=True,
        )
        assert response.status_code == HTTPStatus.FOUND


class EditProductTestCase(MarketAccessTestCase):
    def test_edit_product_has_initial_data(self):
        response = self.client.get(
            reverse("barriers:edit_product", kwargs={"barrier_id": self.barrier["id"]})
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["product"] == self.barrier["product"]

    @patch("utils.api.resources.APIResource.patch")
    def test_product_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse("barriers:edit_product", kwargs={"barrier_id": self.barrier["id"]}),
            data={"product": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "product" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_product_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse("barriers:edit_product", kwargs={"barrier_id": self.barrier["id"]}),
            data={"product": "New product"},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            product="New product",
        )
        assert response.status_code == HTTPStatus.FOUND


class EditSourceTestCase(MarketAccessTestCase):
    def test_edit_source_has_initial_data(self):
        response = self.client.get(
            reverse("barriers:edit_source", kwargs={"barrier_id": self.barrier["id"]})
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["source"] == self.barrier["source"]["code"]

    @patch("utils.api.resources.APIResource.patch")
    def test_source_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse("barriers:edit_source", kwargs={"barrier_id": self.barrier["id"]}),
            data={"source": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "source" in form.errors
        assert "other_source" not in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_other_source_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse("barriers:edit_source", kwargs={"barrier_id": self.barrier["id"]}),
            data={"source": "OTHER"},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "source" not in form.errors
        assert "other_source" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_bad_source_gets_error(self, mock_patch):
        response = self.client.post(
            reverse("barriers:edit_source", kwargs={"barrier_id": self.barrier["id"]}),
            data={"source": "NOTAVALIDSOURCE"},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "source" in form.errors
        assert "other_source" not in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_source_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse("barriers:edit_source", kwargs={"barrier_id": self.barrier["id"]}),
            data={"source": "TRADE", "other_source": "don't save this"},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            source="TRADE",
            other_source="",
        )
        assert response.status_code == HTTPStatus.FOUND

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_source_calls_api_with_other_source(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse("barriers:edit_source", kwargs={"barrier_id": self.barrier["id"]}),
            data={"source": "OTHER", "other_source": "Some source"},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            source="OTHER",
            other_source="Some source",
        )
        assert response.status_code == HTTPStatus.FOUND


class EditTagsTestCase(MarketAccessTestCase):
    def test_edit_tags_has_initial_data(self):
        response = self.client.get(
            reverse("barriers:edit_tags", kwargs={"barrier_id": self.barrier["id"]})
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]

        test_tag_list = []
        for tag in self.barrier["tags"]:
            test_tag_list.append(tag["id"])
        assert form.initial["tags"] == test_tag_list
        assert form.initial["top_barrier"] == TOP_PRIORITY_BARRIER_STATUS.APPROVED

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.UsersResource.get_current")
    def test_edit_tags_calls_api(self, mock_user, mock_patch):
        mock_user.return_value = self.administrator
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse("barriers:edit_tags", kwargs={"barrier_id": self.barrier["id"]}),
            data={
                "tags": [1],
            },
        )

        mock_patch.assert_called_with(
            id=self.barrier["id"],
            tags=[
                "1",
            ],
        )
        assert response.status_code == HTTPStatus.FOUND


class EditPriorityTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.BarriersResource.get_top_priority_summary")
    def test_edit_priority_has_initial_data(self, mock_priority_get):
        mock_priority_get.return_value = self.barrier["top_priority_summary"]
        response = self.client.get(
            reverse("barriers:edit_priority", kwargs={"barrier_id": self.barrier["id"]})
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["priority_level"] == self.barrier["priority_level"]
        assert form.initial["top_barrier"] == TOP_PRIORITY_BARRIER_STATUS.APPROVED

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.BarriersResource.get_top_priority_summary")
    def test_priority_cannot_be_empty(self, mock_priority_get, mock_patch):
        mock_priority_get.return_value = self.barrier["top_priority_summary"]
        response = self.client.post(
            reverse(
                "barriers:edit_priority", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"priority": "", "priority_summary": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "priority_level" in form.errors
        assert form.errors["priority_level"] == ["Select a priority type"]
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.BarriersResource.get_top_priority_summary")
    def test_bad_priority_gets_error(self, mock_priority_get, mock_patch):
        mock_priority_get.return_value = self.barrier["top_priority_summary"]
        response = self.client.post(
            reverse(
                "barriers:edit_priority", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"priority_level": "MEOW", "priority_summary": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "priority_level" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.UsersResource.get_current")
    @patch("utils.api.resources.BarriersResource.get_top_priority_summary")
    @patch("utils.api.resources.BarriersResource.create_top_priority_summary")
    def test_edit_priority_calls_api(
        self, mock_priority_patch, mock_priority_get, mock_user, mock_patch
    ):
        self.barrier["top_priority_status"] = "NONE"
        mock_user.return_value = self.administrator
        mock_patch.return_value = self.barrier
        mock_priority_get.return_value = {"top_priority_summary_text": "", "id": ""}
        response = self.client.post(
            reverse(
                "barriers:edit_priority", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={
                "priority_level": "WATCHLIST",
                "top_barrier": TOP_PRIORITY_BARRIER_STATUS.NONE,
            },
        )

        mock_priority_patch.assert_not_called()

        mock_patch.assert_called_with(
            id=self.barrier["id"],
            priority_level="WATCHLIST",
            tags=[1],
            top_priority_status="NONE",
        )
        assert response.status_code == HTTPStatus.FOUND

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.UsersResource.get_current")
    @patch("utils.api.resources.BarriersResource.get_top_priority_summary")
    @patch("utils.api.resources.BarriersResource.patch_top_priority_summary")
    def test_edit_priority_calls_api_with_summary(
        self, mock_priority_patch, mock_priority_get, mock_user, mock_patch
    ):
        mock_user.return_value = self.administrator
        mock_patch.return_value = self.barrier
        mock_priority_get.return_value = self.barrier["top_priority_summary"]
        response = self.client.post(
            reverse(
                "barriers:edit_priority", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={
                "priority_level": "REGIONAL",
                "priority_summary": "New summary",
                "top_barrier": TOP_PRIORITY_BARRIER_STATUS.NONE,
            },
        )

        mock_priority_patch.assert_called_with(
            top_priority_summary_text="New summary",
            barrier=self.barrier["id"],
        )

        mock_patch.assert_called_with(
            id=self.barrier["id"],
            priority_level="REGIONAL",
            tags=[1],
            top_priority_status=TOP_PRIORITY_BARRIER_STATUS.NONE,
        )
        assert response.status_code == HTTPStatus.FOUND

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.UsersResource.get_current")
    @patch("utils.api.resources.BarriersResource.create_top_priority_summary")
    @patch("utils.api.resources.BarriersResource.get_top_priority_summary")
    def test_top_priority_barrier_to_watchlist_changes_to_removal_pending(
        self, mock_priority_get, mock_priority_patch, mock_user, mock_patch
    ):
        mock_user.return_value = self.administrator
        mock_patch.return_value = self.barrier
        mock_priority_get.return_value = self.barrier["top_priority_summary"]
        response = self.client.post(
            reverse(
                "barriers:edit_priority", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={
                "priority_level": "WATCHLIST",
                "top_barrier": "APPROVED",
                "priority_summary": "Barrier of extreme importance",
            },
        )

        mock_priority_patch.assert_not_called()

        mock_patch.assert_called_with(
            id=self.barrier["id"],
            priority_level="WATCHLIST",
            tags=[1],
            top_priority_status="REMOVAL_PENDING",
        )
        assert response.status_code == HTTPStatus.FOUND

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.UsersResource.get_current")
    def test_approval_pending_barrier_to_watchlist_cancels_request(
        self, mock_user, mock_patch
    ):
        self.barrier["top_priority_status"] = "APPROVAL_PENDING"
        mock_user.return_value = self.administrator
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_priority", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={
                "priority_level": "WATCHLIST",
            },
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            priority_level="WATCHLIST",
            tags=[1],
            top_priority_status="NONE",
            top_priority_rejection_summary="",
        )
        assert response.status_code == HTTPStatus.FOUND


class EditTermTestCase(MarketAccessTestCase):
    def test_edit_term_has_initial_data(self):
        response = self.client.get(
            reverse(
                "barriers:edit_term",
                kwargs={"barrier_id": self.barrier["id"]},
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["term"] == self.barrier["term"]["id"]

    @patch("utils.api.resources.APIResource.patch")
    def test_term_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_term",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"term": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "term" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_bad_data_gets_error(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_term",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"term": "3"},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "term" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_term_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_term",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"term": "1"},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            term="1",
        )
        assert response.status_code == HTTPStatus.FOUND


class EditEstimatedResolutionDateTestCase(MarketAccessTestCase):
    def test_edit_estimated_resolution_date_has_initial_data(self):
        response = self.client.get(
            reverse(
                "barriers:edit_estimated_resolution_date",
                kwargs={"barrier_id": self.barrier["id"]},
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["estimated_resolution_date"] == dateutil.parser.parse(
            self.barrier["estimated_resolution_date"]
        )

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.UsersResource.get_current")
    def test_estimated_resolution_date_cannot_be_empty(self, mock_user, mock_patch):
        mock_user.return_value = self.administrator
        response = self.client.post(
            reverse(
                "barriers:edit_estimated_resolution_date",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "estimated_resolution_date" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.UsersResource.get_current")
    def test_estimated_resolution_date_bad_data_gets_error(self, mock_user, mock_patch):
        mock_user.return_value = self.administrator
        response = self.client.post(
            reverse(
                "barriers:edit_estimated_resolution_date",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "estimated_resolution_date_0": "50",
                "estimated_resolution_date_1": "2022",
            },
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "estimated_resolution_date" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.UsersResource.get_current")
    def test_estimated_resolution_date_incomplete_data_gets_error(
        self, mock_user, mock_patch
    ):
        mock_user.return_value = self.administrator
        response = self.client.post(
            reverse(
                "barriers:edit_estimated_resolution_date",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "estimated_resolution_date_0": "",
                "estimated_resolution_date_1": "2022",
            },
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "estimated_resolution_date" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.UsersResource.get_current")
    def test_edit_estimated_resolution_date_calls_api(self, mock_user, mock_patch):
        mock_user.return_value = self.administrator
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_estimated_resolution_date",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "estimated_resolution_date_0": "6",
                "estimated_resolution_date_1": "2022",
            },
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            estimated_resolution_date="2022-06-01",
            proposed_estimated_resolution_date="2022-06-01",
            estimated_resolution_date_change_reason="",
        )
        assert response.status_code == HTTPStatus.FOUND

    @patch("utils.api.resources.APIResource.patch")
    @patch("utils.api.resources.UsersResource.get_current")
    def test_clear_estimated_resolution_date_calls_api(self, mock_user, mock_patch):
        mock_user.return_value = self.administrator
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_estimated_resolution_date",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "estimated_resolution_date_0": "6",
                "estimated_resolution_date_1": "2022",
                "clear": "1",
            },
        )
        print(response)
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            estimated_resolution_date=None,
            proposed_estimated_resolution_date=None,
            estimated_resolution_date_change_reason="",
        )
        assert response.status_code == HTTPStatus.FOUND


class EditCausedByTradingBlocTestCase(MarketAccessTestCase):
    barrier_index = 1

    def setUp(self):
        super().setUp()
        self.url = reverse(
            "barriers:edit_caused_by_trading_bloc",
            kwargs={"barrier_id": self.barrier["id"]},
        )

    def test_edit_caused_by_trading_bloc_has_initial_data(self):
        response = self.client.get(self.url)
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert (
            form.initial["caused_by_trading_bloc"]
            == self.barrier["caused_by_trading_bloc"]
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_caused_by_trading_bloc_cannot_be_empty(self, mock_patch):
        response = self.client.post(self.url, data={"caused_by_trading_bloc": ""})
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "caused_by_trading_bloc" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_caused_by_trading_bloc_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(self.url, data={"caused_by_trading_bloc": "yes"})
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            caused_by_trading_bloc=True,
        )
        assert response.status_code == HTTPStatus.FOUND
