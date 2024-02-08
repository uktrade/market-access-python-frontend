from http import HTTPStatus

from django.urls import reverse
from mock import patch

from core.tests import MarketAccessTestCase


class TestDownloadBarriers(MarketAccessTestCase):
    @patch("utils.api.client.BarrierDownloadsResource.get_presigned_url")
    def test_download_barriers(self, mock_get_presigned_url):
        mock_get_presigned_url.return_value = {
            "presigned_url": "http://s3.example-download.com"
        }
        response = self.client.get(
            reverse("barriers:download-link"),
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
                "status": ["2", "5"],
                "user": "1",
                "ordering": "-reported",
            },
        )
        assert response.status_code == HTTPStatus.FOUND

        mock_get_presigned_url.assert_called_with(
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
            status="2,5",
            user="1",
            archived="0",
            ordering="-reported",
        )

    @patch("utils.api.client.BarriersResource.get_presigned_url")
    def test_download_response_contains_correct_url_encoding(
        self, mock_get_presigned_url
    ):
        # tss-1359 - filters missing after download redirect
        mock_get_presigned_url.return_value = {
            "presigned_url": "http://s3.example-download.com"
        }
        response = self.client.get(
            reverse("barriers:download-link"),
            data={
                "search": "Test search",
                "country": [
                    "9f5f66a0-5d95-e211-a939-e4115bead28a",
                    "83756b9a-5d95-e211-a939-e4115bead28a",
                ],
                "ordering": "-reported",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert "search_csv_downloaded=1" in response.url
        assert "&country=9f5f66a0-5d95-e211-a939-e4115bead28a" in response.url
        assert "&country=83756b9a-5d95-e211-a939-e4115bead28a" in response.url
