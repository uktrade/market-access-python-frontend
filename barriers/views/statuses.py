from django.urls import reverse
from django.views.generic import FormView

from barriers.forms.statuses import BarrierChangeStatusForm

from .mixins import BarrierMixin


class BarrierChangeStatus(BarrierMixin, FormView):
    template_name = "barriers/edit/status/change.html"
    form_class = BarrierChangeStatusForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        form = context_data["form"]
        context_data.update(
            {
                "barrier": self.barrier,
                "valid_status_values": [
                    choice[0] for choice in form.fields["status"].choices
                ],
            }
        )
        return context_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier"] = self.barrier
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
