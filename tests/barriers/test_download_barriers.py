from http import HTTPStatus

from django.urls import reverse

from core.tests import MarketAccessTestCase

from mock import patch


class DownloadBarriersTestCase(MarketAccessTestCase):
    @patch("utils.api.client.BarriersResource.get_csv")
    def test_download_barriers(self, mock_get_csv):
        response = self.client.get(
            reverse("barriers:download"),
            data={
                "search": "Test search",
                "country": [
                    "9f5f66a0-5d95-e211-a939-e4115bead28a",
                    "83756b9a-5d95-e211-a939-e4115bead28a",
                ],
                "sector": [
                    "9538cecc-5f95-e211-a939-e4115bead28a",
                    "aa22c9d2-5f95-e211-a939-e4115bead28a",
                ],
                "category": ["130", "141"],
                "region": [
                    "3e6809d6-89f6-4590-8458-1d0dab73ad1a",
                    "5616ccf5-ab4a-4c2c-9624-13c69be3c46b",
                ],
                "priority": ["HIGH", "MEDIUM"],
                "status": ["1", "2", "7"],
                "user": "1",
            },
        )
        assert response.status_code == HTTPStatus.OK

        mock_get_csv.assert_called_with(
            search="Test search",
            location=(
                "9f5f66a0-5d95-e211-a939-e4115bead28a,"
                "83756b9a-5d95-e211-a939-e4115bead28a,"
                "3e6809d6-89f6-4590-8458-1d0dab73ad1a,"
                "5616ccf5-ab4a-4c2c-9624-13c69be3c46b"
            ),
            sector=(
                "9538cecc-5f95-e211-a939-e4115bead28a,"
                "aa22c9d2-5f95-e211-a939-e4115bead28a"
            ),
            category="130,141",
            priority="HIGH,MEDIUM",
            status="1,2,7",
            user="1",
            archived="0",
            ordering="-reported_on",
        )
