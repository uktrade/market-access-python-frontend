from django.views.generic import TemplateView

from utils.api_client import MarketAccessAPIClient


class Dashboard(TemplateView):
    template_name = "barriers/dashboard.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update({
            'page': 'dashboard',
        })
        return context_data


class AddABarrier(TemplateView):
    template_name = "barriers/add_a_barrier.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update({
            'page': 'add-a-barrier',
        })
        return context_data


class FindABarrier(TemplateView):
    template_name = "barriers/find_a_barrier.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        client = MarketAccessAPIClient()
        barriers = client.barriers.list(ordering="-reported_on", limit=100, offset=0)

        context_data.update({
            'barriers': barriers,
            'page': 'find-a-barrier',
        })
        return context_data


class BarrierDetail(TemplateView):
    template_name = "barriers/barrier_detail.html"

    def get_context_data(self, **kwargs):
        client = MarketAccessAPIClient()
        uuid = self.kwargs.get('id')
        barrier = client.barriers.get(id=uuid)

        return {
            'barrier': barrier,
        }
