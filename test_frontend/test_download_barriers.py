import pytest


@pytest.mark.order(1)
def test_download_barrier_csv_from_my_downloads_tab(page):
    pass


@pytest.mark.order(2)
def test_downloads_details_page(page):
    pass


@pytest.mark.order(3)
def test_clicking_download_button_search_page(page):
    pass


@pytest.mark.order(4)
def test_clicking_download_button_on_saved_search_page(page):
    pass
