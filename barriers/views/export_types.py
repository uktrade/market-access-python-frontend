from django.urls import reverse
from django.views.generic import FormView

from reports.report_barrier_forms import BarrierExportTypeForm
from utils.api.client import MarketAccessAPIClient
from utils.metadata import MetadataMixin
from .mixins import BarrierMixin


class BarrierEditExportType(MetadataMixin, BarrierMixin, FormView):
    template_name = "barriers/edit/export_type.html"
    form_class = BarrierExportTypeForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        export_types = self.request.session.get("export_types", [])

        context_data.update(
            {
                "export_types": export_types,
                "has_all_export_types_selected": len(export_types) == 3,
            }
        )
        return context_data

    def form_valid(self, form):
        client = MarketAccessAPIClient(form.token)
        client.barriers.patch(
            id=form.barrier_id,
            export_types=form.cleaned_data["export_types"],
            export_description=form.cleaned_data["export_description"]
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )

    def get_initial(self):
        initial = super().get_initial()
        initial["export_types"] = [each["name"] for each in self.barrier.export_types]
        initial["export_description"] = self.barrier.export_description
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["barrier_id"] = str(self.kwargs.get("barrier_id"))
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs


class BarrierEditExportTypeSession(BarrierEditExportType):
    use_session_export_types = True
