from django.http import HttpResponseRedirect
from django.views.generic import FormView

from .mixins import APIBarrierFormViewMixin
from barriers.forms.wto import WTOInfoForm, WTOStatusForm

from utils.metadata import get_metadata


class EditWTOStatus(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/wto/status.html"
    form_class = WTOStatusForm

    def form_valid(self, form):
        if (
            form.cleaned_data.get("wto_notified") is True or
            form.cleaned_data.get("wto_should_be_notified") is True
        ):
            return HttpResponseRedirect(self.get_continue_url())

    def get_continue_url(self):
        return reverse(
            "barriers:edit_wto_info",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )

    # def get_initial(self):
    #     return {"wto_status": self.barrier.barrier_title}


class EditWTOInfo(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/wto/info.html"
    form_class = WTOInfoForm
