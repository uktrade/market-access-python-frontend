from django.views.generic import TemplateView
from utils.metadata import MetadataMixin
from utils.api.client import MarketAccessAPIClient

class RelatedBarriersView(MetadataMixin, TemplateView):
    """View for the similar barriers page."""
    template_name = "barriers/similar_barriers.html"
    _client = None

    @property
    def client(self):
        if self._client is None:
            self._client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        return self._client
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context["similar_barriers"] = self.get_similar_barriers(kwargs["barrier_id"])
        return self.render_to_response(context)

    def get_related_barriers(self, barrier_id):
        return self.client.barriers.get_similar(barrier_id)
