# add and edit views for progress updates
from django.views.generic import FormView, TemplateView

from barriers.forms.edit import UpdateBarrierProgressUpdateForm
from barriers.views.mixins import APIBarrierFormViewMixin, BarrierMixin


class BarrierAddProgressUpdate(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/progress_updates/add.html"
    form_class = UpdateBarrierProgressUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        return kwargs


class BarrierEditProgressUpdate(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/progress_updates/edit.html"
    form_class = UpdateBarrierProgressUpdateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier_id"] = str(self.kwargs.get("barrier_id"))
        kwargs["progress_update_id"] = str(self.kwargs.get("progress_update_id"))
        return kwargs

    def get_initial(self):
        progress_update = next(
            (
                item
                for item in self.barrier.progress_updates
                if item["id"] == str(self.kwargs.get("progress_update_id"))
            ),
            None,
        )
        updates = self.barrier.progress_updates
        progress_update_id = self.kwargs.get("progress_update_id")
        return {
            "status": progress_update["status"],
            "update": progress_update["message"],
            "next_steps": progress_update["next_steps"],
        }


class BarrierListProgressUpdate(BarrierMixin, TemplateView):
    template_name = "barriers/progress_updates/list.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data.update(
            {
                "page": "progress_updates",
                "progress_updates": self.barrier.progress_updates,
            }
        )
        return context_data
