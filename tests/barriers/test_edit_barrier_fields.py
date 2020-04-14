from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from mock import patch


class EditTitleTestCase(MarketAccessTestCase):
    def test_edit_title_has_initial_data(self):
        response = self.client.get(
            reverse("barriers:edit_title", kwargs={"barrier_id": self.barrier["id"]})
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["title"] == self.barrier["barrier_title"]

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
            id=self.barrier["id"], barrier_title="New Title",
        )
        assert response.status_code == HTTPStatus.FOUND


class EditSummaryTestCase(MarketAccessTestCase):
    def test_edit_summary_has_initial_data(self):
        response = self.client.get(
            reverse(
                "barriers:edit_summary", kwargs={"barrier_id": self.barrier["id"]}
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["summary"] == self.barrier["summary"]

    @patch("utils.api.resources.APIResource.patch")
    def test_summary_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_summary", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"summary": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "summary" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_summary_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_summary", kwargs={"barrier_id": self.barrier["id"]}
            ),
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
            id=self.barrier["id"], product="New product",
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
        assert form.initial["source"] == self.barrier["source"]

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
            id=self.barrier["id"], source="TRADE", other_source=None,
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
            id=self.barrier["id"], source="OTHER", other_source="Some source",
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
            data={"priority": "LOW", "priority_summary": ""},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"], priority="LOW", priority_summary=None,
        )
        assert response.status_code == HTTPStatus.FOUND

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_priority_calls_api_with_summary(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_priority", kwargs={"barrier_id": self.barrier["id"]}
            ),
            data={"priority": "HIGH", "priority_summary": "New summary"},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"], priority="HIGH", priority_summary="New summary",
        )
        assert response.status_code == HTTPStatus.FOUND


class EditProblemStatusTestCase(MarketAccessTestCase):
    def test_edit_problem_status_has_initial_data(self):
        response = self.client.get(
            reverse(
                "barriers:edit_problem_status",
                kwargs={"barrier_id": self.barrier["id"]},
            )
        )
        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["problem_status"] == self.barrier["problem_status"]

    @patch("utils.api.resources.APIResource.patch")
    def test_problem_status_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_problem_status",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"problem_status": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "problem_status" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_bad_data_gets_error(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:edit_problem_status",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"problem_status": "3"},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "problem_status" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_edit_problem_status_calls_api(self, mock_patch):
        mock_patch.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:edit_problem_status",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"problem_status": "1"},
        )
        mock_patch.assert_called_with(
            id=self.barrier["id"], problem_status="1",
        )
        assert response.status_code == HTTPStatus.FOUND
