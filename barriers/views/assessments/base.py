from django.urls import reverse
from django.views.generic import FormView

from ..mixins import BarrierMixin


class ArchiveAssessmentBase(BarrierMixin, FormView):
    template_name = "barriers/assessments/archive.html"
    title = "Archive assessment"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["title"] = self.title
        return context_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["id"] = self.kwargs["assessment_id"]
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:assessment_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
