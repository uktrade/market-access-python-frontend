from http import HTTPStatus

from django.urls import reverse
from mock import patch

from barriers.models import BarrierDownload
from core.tests import MarketAccessTestCase


class TestDownloadBarriers(MarketAccessTestCase):
    @patch("utils.api.client.BarrierDownloadsResource.get_presigned_url")
    def test_download_barriers(self, mock_get_presigned_url):
        mock_get_presigned_url.return_value = {
            "presigned_url": "http://s3.example-download.com"
        }
        download_id = "83756b9a-5d95-e211-a939-e4115bead28a"
        response = self.client.get(
            reverse(
                "barriers:download-link", kwargs={"download_barrier_id": download_id}
            ),
        )
        assert response.status_code == HTTPStatus.FOUND

        mock_get_presigned_url.assert_called_with(download_id)

    @patch("utils.api.client.BarrierDownloadsResource.create")
    def test_create_download(self, mock_create):
        data = {
            "id": "83756b9a-5d95-e211-a939-e4115bead28a",
            "status": "PENDING",
            "name": "Test search",
            "filename": "test-search.csv",
            "created_on": "2020-01-01T00:00:00Z",
            "modified_on": "2020-01-01T00:00:00Z",
            "filters": {
                "search": "Test search",
                "country": [
                    "9f5f66a0-5d95-e211-a939-e4115bead28a",
                    "83756b9a-5d95-e211-a939-e4115bead28a",
                ],
                "ordering": "-reported",
            },
            "count": 10,
        }
        mock_create.return_value = BarrierDownload(data)
        response = self.client.get(
            reverse("barriers:download"),
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
        assert response.url == (
            f"/search/download/{data['id']}?search_csv_downloaded=&search_csv_download_error="
        )

        mock_create.assert_called_with(
            **{
                "search": "Test search",
                "location": "9f5f66a0-5d95-e211-a939-e4115bead28a,83756b9a-5d95-e211-a939-e4115bead28a",
                "archived": "0",
                "ordering": "-reported",
                "filters": {
                    "search": "Test search",
                    "country": [
                        "9f5f66a0-5d95-e211-a939-e4115bead28a",
                        "83756b9a-5d95-e211-a939-e4115bead28a",
                    ],
                },
            }
        )

    @patch("utils.api.client.BarrierDownloadsResource.create")
    def test_download_response_response_url_value(self, mock_create):
        # tss-1359 - filters missing after download redirect

        data = {
            "id": "83756b9a-5d95-e211-a939-e4115bead28a",
            "status": "PENDING",
            "name": "Test search",
            "filename": "test-search.csv",
            "created_on": "2020-01-01T00:00:00Z",
            "modified_on": "2020-01-01T00:00:00Z",
            "filters": {
                "search": "Test search",
                "country": [
                    "9f5f66a0-5d95-e211-a939-e4115bead28a",
                    "83756b9a-5d95-e211-a939-e4115bead28a",
                ],
                "ordering": "-reported",
            },
            "count": 10,
        }
        mock_create.return_value = BarrierDownload(data)

        response = self.client.get(
            reverse("barriers:download"),
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
        assert response.url == (
            f"/search/download/{data['id']}?search_csv_downloaded=&search_csv_download_error="
        )
