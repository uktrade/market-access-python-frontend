from django.views.generic import TemplateView

from utils.api.client import MarketAccessAPIClient

from .mixins import BarrierMixin


class BarrierHistory(BarrierMixin, TemplateView):
    template_name = "barriers/history.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        full_history = self.get_full_history()

        for item in full_history[:]:
            # This loop allows us to exclude certain history items from the display if un-wanted

            # Top priority fields should only be included for accepted and removed tags
            if item.field == "top_priority_status":
                if item.data["new_value"] is None or item.data["new_value"][
                    "value"
                ] not in ["APPROVED", "REMOVED"]:
                    full_history.remove(item)

        context_data["history_items"] = full_history
        return context_data

    def get_full_history(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        barrier_id = self.kwargs.get("barrier_id")
        full_history = client.barriers.get_full_history(barrier_id=barrier_id)
        full_history.sort(key=lambda object: object.date, reverse=True)
        return full_history
