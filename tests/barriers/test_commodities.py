from http import HTTPStatus

from django.urls import reverse
from mock import Mock, patch

from barriers.models import Commodity
from core.tests import MarketAccessTestCase
from utils.exceptions import APIHttpException


class CommoditiesTestCase(MarketAccessTestCase):
    country_id = "80756b9a-5d95-e211-a939-e4115bead28a"
    lookup_data = {
        "code_0": "21",
        "code_1": "05",
        "country": country_id,
    }
    commodity_data = {
        "code": "2105000000",
        "code_display": "21.05",
        "description": "Ice cream",
        "full_description": "Ice cream",
    }
    barrier_commodity_data = {
        "code": "2105009900",
        "code_display": "2105.00.99",
        "country": {"id": country_id},
        "commodity": commodity_data,
    }

    @patch("utils.api.resources.CommoditiesResource.get")
    def test_empty_commodity_lookup(self, mock_get):
        response = self.client.get(
            reverse("barriers:edit_commodities", kwargs={"barrier_id": self.barrier["id"]}),
            {
                "code_0": "",
                "country": self.country_id,
            }
        )
        assert response.status_code == HTTPStatus.OK
        assert "lookup_form" in response.context
        form = response.context["lookup_form"]
        assert form.is_valid() is False
        assert mock_get.called is False

    @patch("utils.api.resources.CommoditiesResource.get")
    def test_commodity_lookup(self, mock_get):
        response = self.client.get(
            reverse("barriers:edit_commodities", kwargs={"barrier_id": self.barrier["id"]}),
            self.lookup_data,
        )
        assert response.status_code == HTTPStatus.OK
        assert "lookup_form" in response.context
        form = response.context["lookup_form"]
        assert form.is_valid() is True
        mock_get.assert_called_with(id="2105000000")

    @patch("utils.api.resources.CommoditiesResource.get")
    def test_ajax_commodity_lookup(self, mock_get):
        mock_get.return_value = Commodity(self.commodity_data)
        response = self.client.get(
            reverse("barriers:edit_commodities", kwargs={"barrier_id": self.barrier["id"]}),
            {"code": "21050099", "country": self.country_id},
            **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        )
        assert response.status_code == HTTPStatus.OK
        mock_get.assert_called_with(id="2105000000")
        response_data = response.json()
        assert response_data == {
            "status": "ok",
            "data": self.barrier_commodity_data,
        }

    @patch("utils.api.resources.CommoditiesResource.get", side_effect=APIHttpException(Mock()))
    def test_ajax_commodity_not_found(self, mock_get):
        response = self.client.get(
            reverse("barriers:edit_commodities", kwargs={"barrier_id": self.barrier["id"]}),
            {"code": "99999999", "country": self.country_id},
            **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        )
        assert response.status_code == HTTPStatus.OK
        mock_get.assert_called_with(id="9999990000")
        response_data = response.json()
        assert response_data == {"status": "error", "message": "Code not found"}

    @patch("utils.api.resources.CommoditiesResource.list")
    def test_ajax_multiple_commodity_lookup(self, mock_list):
        mock_list.return_value = [Commodity(self.commodity_data)]
        response = self.client.get(
            reverse("barriers:edit_commodities", kwargs={"barrier_id": self.barrier["id"]}),
            {"codes": "21050099,2106,2107", "country": self.country_id},
            **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        )
        assert response.status_code == HTTPStatus.OK
        kwargs_codes = mock_list.call_args.kwargs.get("codes", "").split(",")
        assert set(kwargs_codes) == set(["2105000000","2107000000","2106000000"])

        response_data = response.json()
        assert response_data == {
            "status": "ok",
            "data": [self.barrier_commodity_data],
        }

    @patch("utils.api.resources.APIResource.patch")
    def test_submit_commodities_form(self, mock_patch):
        response = self.client.post(
            reverse("barriers:edit_commodities", kwargs={"barrier_id": self.barrier["id"]}),
            data={
                "action": "save",
                "codes": ["2105009900", "0708000000"],
                "countries": [self.country_id, self.country_id],
            },
        )
        assert response.status_code == HTTPStatus.FOUND

        mock_patch.assert_called_with(
            id=self.barrier["id"],
            commodities=[
                {'code': '2105009900', 'country': '80756b9a-5d95-e211-a939-e4115bead28a'},
                {'code': '0708000000', 'country': '80756b9a-5d95-e211-a939-e4115bead28a'},
            ],
        )

    @patch("utils.api.resources.APIResource.patch")
    def test_confirm_commodity(self, mock_patch):
        session_key = f"barrier:{self.barrier['id']}:commodities"
        self.update_session({session_key: []})
        response = self.client.post(
            reverse("barriers:edit_commodities", kwargs={"barrier_id": self.barrier["id"]}),
            data={
                "confirm-commodity": "1",
                "code": "2105009900",
                "country": self.country_id,
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert mock_patch.called is False

        assert self.client.session[session_key] == [
            {"code": "2105009900", "country": self.country_id}
        ]

    @patch("utils.api.resources.CommoditiesResource.list")
    @patch("utils.api.resources.APIResource.patch")
    def test_remove_commodity(self, mock_patch, mock_list):
        mock_list.return_value = [Commodity(self.commodity_data)]
        session_key = f"barrier:{self.barrier['id']}:commodities"
        self.update_session({
            session_key: [
                {"code": "2105009900", "country": self.country_id},
                {"code": "0708000000", "country": self.country_id},
            ]
        })
        response = self.client.post(
            reverse("barriers:edit_commodities", kwargs={"barrier_id": self.barrier["id"]}),
            data={"remove-commodity": "2105009900"},
        )
        assert response.status_code == HTTPStatus.OK
        assert mock_patch.called is False

        session_codes = [
            commodity["code"] for commodity in self.client.session[session_key]
        ]
        assert session_codes == ["0708000000"]

    def test_cancel_commodity_form(self):
        session_key = f"barrier:{self.barrier['id']}:commodities"
        self.update_session({
            session_key: [{"code": "2105009900", "country": self.country_id},]
        })
        response = self.client.post(
            reverse("barriers:edit_commodities", kwargs={"barrier_id": self.barrier["id"]}),
            data={"action": "cancel"},
        )
        assert response.status_code == HTTPStatus.FOUND
        assert session_key not in self.client.session
