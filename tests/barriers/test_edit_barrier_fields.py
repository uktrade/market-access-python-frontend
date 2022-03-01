import logging
from http import HTTPStatus

import dateutil.parser
from django.urls import reverse
from mock import patch

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


class EditPriorityTestCase(MarketAccessTestCase):
    def test_edit_priority_has_initial_data(self):
        response = self.client.get(
            reverse("barriers:edit_priority", kwargs={"barrier_id": self.barrier["id"]})
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["priority"] == self.barrier["priority"]["code"]
        assert form.initial["top_barrier"] == "Yes"

    @patch("utils.api.resources.APIResource.patch")
    def test_priority_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_priority", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"priority": "", "priority_summary": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "priority" in form.errors
        assert "priority_summary" not in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_bad_priority_gets_error(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_priority", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"priority": "MEOW", "priority_summary": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "priority" in form.errors
        assert "priority_summary" not in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_priority_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_priority", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"priority": "LOW", "priority_summary": "", "top_barrier": "Yes"},
        )

        mock_patch.assert_called_with(
            id=self.barrier["id"],
            priority="LOW",
            priority_summary="",
            tags=[1, 4],
        )
        assert response.status_code == HTTPStatus.FOUND

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_priority_calls_api_with_summary(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_priority", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={
                "priority": "HIGH",
                "top_barrier": "No",
                "priority_summary": "New summary",
            },
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            priority="HIGH",
            tags=[1],
            priority_summary="New summary",
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


class EditEndDateTestCase(MarketAccessTestCase):
    def test_edit_end_date_has_initial_data(self):
        response = self.client.get(
            reverse(
                "barriers:edit_end_date",
                kwargs={"barrier_id": self.barrier["id"]},
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["end_date"] == dateutil.parser.parse(
            self.barrier["end_date"]
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_end_date_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_end_date",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "end_date" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_end_date_bad_data_gets_error(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_end_date",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "end_date_0": "50",
                "end_date_1": "1",
                "end_date_2": "2022",
            },
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "end_date" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_end_date_incomplete_data_gets_error(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_end_date",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "end_date_0": "24",
                "end_date_1": "",
                "end_date_2": "2022",
            },
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "end_date" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_end_date_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_end_date",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "end_date_0": "25",
                "end_date_1": "6",
                "end_date_2": "2022",
            },
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            end_date="2022-06-25",
        )
        assert response.status_code == HTTPStatus.FOUND

    @patch("utils.api.resources.APIResource.patch")
    def test_clear_end_date_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_end_date",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "end_date_0": "25",
                "end_date_1": "6",
                "end_date_2": "2022",
                "clear": "1",
            },
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"],
            end_date=None,
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
