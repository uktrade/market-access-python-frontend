from http import HTTPStatus

from django.urls import resolve, reverse
from mock import patch

from barriers.views.public_barriers import PublicBarrierDetail
from core.tests import MarketAccessTestCase


class PublicBarrierViewTestCase(MarketAccessTestCase):

    def test_public_barrier_url_resolves_to_correct_view(self):
        match = resolve(f'/barriers/{self.barrier["id"]}/public/')
        assert match.func.view_class == PublicBarrierDetail

    @patch("utils.api.client.PublicBarriersResource.get")
    @patch("utils.api.client.PublicBarriersResource.get_activity")
    @patch("utils.api.client.PublicBarriersResource.get_notes")
    def test_public_barrier_view_loads_correct_template(self, _mock_get_notes, _mock_get_activity, mock_get):
        mock_get.return_value = self.barrier
        url = reverse('barriers:public_barrier_detail', kwargs={"barrier_id": self.barrier["id"]})

        response = self.client.get(url)

        assert HTTPStatus.OK == response.status_code
        self.assertTemplateUsed(response, "barriers/public_barriers/detail.html")

    @patch("utils.api.client.PublicBarriersResource.get")
    @patch("utils.api.client.PublicBarriersResource.get_activity")
    @patch("utils.api.client.PublicBarriersResource.get_notes")
    def test_public_barrier_view_loads_html(self, _mock_get_notes, _mock_get_activity, mock_get):
        mock_get.return_value = self.public_barrier
        url = reverse('barriers:public_barrier_detail', kwargs={"barrier_id": self.barrier["id"]})
        title = '<title>Market Access - Public barrier</title>'
        section_head = '<h2 class="summary-group__heading">Public view:'
        notes_head = '<h2 class="section-heading govuk-!-margin-bottom-0">Internal notes and updates</h2>'
        add_note_button = '<a class="govuk-button button--primary" href="?add-note=1">Add a note</a>'

        response = self.client.get(url)
        html = response.content.decode("utf8")

        assert HTTPStatus.OK == response.status_code
        assert title in html
        assert section_head in html
        assert notes_head in html
        assert add_note_button in html
