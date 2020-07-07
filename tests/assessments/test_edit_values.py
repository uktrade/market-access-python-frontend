from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from mock import patch


class EditEconomyValueTestCase(MarketAccessTestCase):
    def setUp(self):
        self.barrier["has_assessment"] = True
        super().setUp()

    def tearDown(self):
        self.barrier["has_assessment"] = False

    @patch("utils.api.resources.BarriersResource.get_assessment")
    def test_economy_value_has_initial_data(self, mock_get_assessment):
        mock_get_assessment.return_value = self.assessments[0]

        response = self.client.get(
            reverse(
                "barriers:economy_value_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            )
        )

        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["value"] == self.assessments[0].value_to_economy

    @patch("utils.api.resources.BarriersResource.create_assessment")
    @patch("utils.api.resources.BarriersResource.update_assessment")
    @patch("utils.api.resources.BarriersResource.get_assessment")
    def test_economy_value_calls_api(
        self, mock_get_assessment, mock_update, mock_create,
    ):
        mock_get_assessment.return_value = self.assessments[0]

        response = self.client.post(
            reverse(
                "barriers:economy_value_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"value": "500000"},
        )
        mock_update.assert_called_with(
            barrier_id=self.barrier["id"], value_to_economy=500000,
        )
        assert mock_create.called is False
        assert response.status_code == HTTPStatus.FOUND


class NewEconomyValueTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.APIResource.patch")
    def test_economy_value_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:economy_value_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"value": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "value" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_economy_value_bad_data(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:economy_value_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"value": "45xx345"},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "value" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.BarriersResource.create_assessment")
    @patch("utils.api.resources.BarriersResource.update_assessment")
    def test_economy_value_calls_api(self, mock_update, mock_create):
        response = self.client.post(
            reverse(
                "barriers:economy_value_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"value": "600000"},
        )
        mock_create.assert_called_with(
            barrier_id=self.barrier["id"], value_to_economy=600000,
        )
        assert mock_update.called is False
        assert response.status_code == HTTPStatus.FOUND


class EditMarketSizeTestCase(MarketAccessTestCase):
    def setUp(self):
        self.barrier["has_assessment"] = True
        super().setUp()

    def tearDown(self):
        self.barrier["has_assessment"] = False

    @patch("utils.api.resources.BarriersResource.get_assessment")
    def test_market_size_has_initial_data(self, mock_get_assessment):
        mock_get_assessment.return_value = self.assessments[0]

        response = self.client.get(
            reverse(
                "barriers:market_size_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            )
        )

        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["value"] == self.assessments[0].import_market_size

    @patch("utils.api.resources.BarriersResource.create_assessment")
    @patch("utils.api.resources.BarriersResource.update_assessment")
    @patch("utils.api.resources.BarriersResource.get_assessment")
    def test_market_size_calls_api(
        self, mock_get_assessment, mock_update, mock_create,
    ):
        mock_get_assessment.return_value = self.assessments[0]

        response = self.client.post(
            reverse(
                "barriers:market_size_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"value": "500001"},
        )
        mock_update.assert_called_with(
            barrier_id=self.barrier["id"], import_market_size=500001,
        )
        assert mock_create.called is False
        assert response.status_code == HTTPStatus.FOUND


class NewMarketSizeTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.APIResource.patch")
    def test_market_size_bad_value(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:market_size_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"value": "45xx345"},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "value" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_market_size_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:market_size_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"value": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "value" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.BarriersResource.create_assessment")
    @patch("utils.api.resources.BarriersResource.update_assessment")
    def test_market_size_calls_api(self, mock_update, mock_create):
        mock_create.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:market_size_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"value": "600001"},
        )
        mock_create.assert_called_with(
            barrier_id=self.barrier["id"], import_market_size=600001,
        )
        assert mock_update.called is False
        assert response.status_code == HTTPStatus.FOUND


class EditExportValueTestCase(MarketAccessTestCase):
    def setUp(self):
        self.barrier["has_assessment"] = True
        super().setUp()

    def tearDown(self):
        self.barrier["has_assessment"] = False

    @patch("utils.api.resources.BarriersResource.get_assessment")
    def test_export_value_has_initial_data(self, mock_get_assessment):
        mock_get_assessment.return_value = self.assessments[0]

        response = self.client.get(
            reverse(
                "barriers:export_value_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            )
        )

        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["value"] == self.assessments[0].export_value

    @patch("utils.api.resources.BarriersResource.create_assessment")
    @patch("utils.api.resources.BarriersResource.update_assessment")
    @patch("utils.api.resources.BarriersResource.get_assessment")
    def test_export_value_calls_api(
        self, mock_get_assessment, mock_update, mock_create,
    ):
        mock_get_assessment.return_value = self.assessments[0]

        response = self.client.post(
            reverse(
                "barriers:export_value_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"value": "500002"},
        )
        mock_update.assert_called_with(
            barrier_id=self.barrier["id"], export_value=500002,
        )
        assert mock_create.called is False
        assert response.status_code == HTTPStatus.FOUND


class NewExportValueTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.APIResource.patch")
    def test_export_value_bad_value(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:export_value_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"value": "4!99"},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "value" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_export_value_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:export_value_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"value": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "value" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.BarriersResource.create_assessment")
    @patch("utils.api.resources.BarriersResource.update_assessment")
    def test_export_value_calls_api(self, mock_update, mock_create):
        mock_create.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:export_value_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"value": "600002"},
        )
        mock_create.assert_called_with(
            barrier_id=self.barrier["id"], export_value=600002,
        )
        assert mock_update.called is False
        assert response.status_code == HTTPStatus.FOUND


class EditCommercialValueTestCase(MarketAccessTestCase):
    def setUp(self):
        self.barrier["has_assessment"] = True
        super().setUp()

    def tearDown(self):
        self.barrier["has_assessment"] = False

    @patch("utils.api.resources.BarriersResource.get_assessment")
    def test_commercial_value_has_initial_data(self, mock_get_assessment):
        mock_get_assessment.return_value = self.assessments[0]

        response = self.client.get(
            reverse(
                "barriers:commercial_value_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            )
        )

        assert response.status_code == HTTPStatus.OK
        assert "form" in response.context
        form = response.context["form"]
        assert form.initial["value"] == self.assessments[0].commercial_value
        assert form.initial["value_explanation"] == self.assessments[0].commercial_value_explanation

    @patch("utils.api.resources.BarriersResource.create_assessment")
    @patch("utils.api.resources.BarriersResource.update_assessment")
    @patch("utils.api.resources.BarriersResource.get_assessment")
    def test_commercial_value_calls_api(
        self, mock_get_assessment, mock_update, mock_create,
    ):
        """ Both commercial_value and commercial_value_explanation are required """
        mock_get_assessment.return_value = self.assessments[0]

        response = self.client.post(
            reverse(
                "barriers:commercial_value_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={
                "value": "500003",
                "value_explanation": "Wibble, wobble."
            },
        )
        mock_update.assert_called_with(
            barrier_id=self.barrier["id"],
            commercial_value=500003,
            commercial_value_explanation="Wibble, wobble."
        )
        assert mock_create.called is False
        assert response.status_code == HTTPStatus.FOUND


class NewCommercialValueTestCase(MarketAccessTestCase):
    @patch("utils.api.resources.APIResource.patch")
    def test_commercial_value_bad_value(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:commercial_value_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"value": "10-0"},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "value" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.APIResource.patch")
    def test_commercial_value_cannot_be_empty(self, mock_patch):
        response = self.client.post(
            reverse(
                "barriers:commercial_value_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"value": ""},
        )
        assert response.status_code == HTTPStatus.OK
        form = response.context["form"]
        assert form.is_valid() is False
        assert "value" in form.errors
        assert mock_patch.called is False

    @patch("utils.api.resources.BarriersResource.create_assessment")
    @patch("utils.api.resources.BarriersResource.update_assessment")
    def test_commercial_value_calls_api(self, mock_update, mock_create):
        mock_create.return_value = self.barrier
        response = self.client.post(
            reverse(
                "barriers:commercial_value_assessment",
                kwargs={"barrier_id": self.barrier["id"]},
            ),
            data={"value": "600003"},
        )
        mock_create.assert_called_with(
            barrier_id=self.barrier["id"], commercial_value=600003,
        )
        assert mock_update.called is False
        assert response.status_code == HTTPStatus.FOUND
