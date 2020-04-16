from django.urls import reverse
from django.views.generic import FormView

from .mixins import BarrierMixin
from barriers.forms.is_temporary import IsTemporaryForm


class BarrierEditIsTemporary(BarrierMixin, FormView):
    template_name = "barriers/edit/is_temporary.html"
    form_class = IsTemporaryForm

    def get_initial(self):
        return {
            "is_temporary": self.barrier.is_temporary,
            "end_date": self.barrier.end_date,
        }

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
