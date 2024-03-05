from django.views.generic import TemplateView

from utils.api.client import MarketAccessAPIClient
from utils.metadata import MetadataMixin

from .mixins import BarrierMixin


class RelatedBarriersView(MetadataMixin, BarrierMixin, TemplateView):
    """View for the similar barriers page."""

    template_name = "barriers/related_barriers.html"
    _client = None

    @property
    def client(self):
        if self._client is None:
            self._client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        return self._client

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context["related_barriers"] = self.get_related_barriers(kwargs["barrier_id"])
        return self.render_to_response(context)

    def get_related_barriers(self, barrier_id):
        return self.client.barriers.get_similar(barrier_id)
