import pytest

from test_frontend import PlaywrightTestBase


class TestBarrierDownloads(PlaywrightTestBase):

    @classmethod
    def get_my_barrier_downloads_tab(cls):
        pass

    @pytest.mark.order(1)
    def test_download_barrier_csv_from_my_downloads_tab(self):
        pass

    @pytest.mark.order(2)
    def test_downloads_details_page(self):
        pass

    @pytest.mark.order(3)
    def test_clicking_download_button_search_page(self):
        pass

    @pytest.mark.order(4)
    def test_clicking_download_button_on_saved_search_page(self):
        pass
