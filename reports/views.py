from django.urls import reverse_lazy
from django.views.generic import TemplateView

from partials.callout import Callout, CalloutButton
from utils.metadata import get_metadata


class BaseReportView(TemplateView):
    callout = None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["page"] = "add-a-barrier"
        if isinstance(self.callout, Callout):
            context_data["callout"] = self.callout

        return context_data


class NewReport(BaseReportView):
    """
    Landing page where users can initiate to add a barrier.
    """
    template_name = "reports/new_report.html"
    callout = Callout(
        heading="Let us know about a non-tariff barrier to a UK business overseas",
        text="You can save your information and come back later to complete.",
        button=CalloutButton(
            href=reverse_lazy("reports:barrier_status"),
            text="Start now",
            button_type="start",
        )
    )

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        metadata = get_metadata()
        context_data['stages'] = metadata.get_report_stages()
        return context_data


class NewReportBarrierStatus(BaseReportView):
    """
    Add a barrier - Step 1
    """
    template_name = "reports/new_report_barrier_status.html"
