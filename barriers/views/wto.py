from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import FormView

from .mixins import APIBarrierFormViewMixin
from barriers.forms.wto import WTOProfileForm, WTOStatusForm

from utils.metadata import get_metadata


class EditWTOStatus(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/wto/status.html"
    form_class = WTOStatusForm

    def form_valid(self, form):
        form.save()
        if (
            form.cleaned_data.get("wto_has_been_notified") is True or
            form.cleaned_data.get("wto_should_be_notified") is True
        ):
            return HttpResponseRedirect(self.get_continue_url())
        return HttpResponseRedirect(self.get_detail_url())

    def get_continue_url(self):
        return reverse(
            "barriers:edit_wto_profile",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )

    def get_detail_url(self):
        return reverse(
            "barriers:barrier_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )

    def get_initial(self):
        if self.barrier.wto_profile:
            wto_profile = self.barrier.wto_profile
            return {
                "wto_has_been_notified": wto_profile.wto_has_been_notified,
                "wto_should_be_notified": wto_profile.wto_should_be_notified,
            }


class EditWTOProfile(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/wto/profile.html"
    form_class = WTOProfileForm

    def get_initial(self):
        if self.barrier.wto_profile:
            fields = (
                "committee_notified",
                "committee_notification_link",
                "member_states",
                "committee_raised_in",
                "committee_meeting_minutes",
                "raised_date",
                "case_number",
            )
            return {field: self.barrier.wto_profile.data.get(field) for field in fields}
