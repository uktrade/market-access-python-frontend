from django.urls import reverse
from django.views.generic import FormView

from .mixins import APIBarrierFormViewMixin, BarrierMixin
from barriers.constants import Statuses
from barriers.forms.statuses import (
    BarrierChangeStatusForm,
    UpdateBarrierStatusForm,
)


class BarrierEditStatus(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/status.html"
    form_class = UpdateBarrierStatusForm

    def is_barrier_resolved(self):
        return self.object.is_resolved or self.object.is_partially_resolved

    def get_initial(self):
        initial = {'status_summary': self.object.status_summary}

        if self.is_barrier_resolved():
            initial['status_date'] = self.object.status['date']
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_resolved'] = self.is_barrier_resolved()
        return kwargs


class BarrierChangeStatus(BarrierMixin, FormView):
    template_name = "barriers/status.html"
    form_class = BarrierChangeStatusForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        form = context_data['form']
        context_data.update({
            'barrier': self.barrier,
            'OPEN_PENDING_ACTION': Statuses.OPEN_PENDING_ACTION,
            'valid_status_values': [
                choice[0] for choice in form.fields['status'].choices
            ],
        })
        return context_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['token'] = self.request.session.get('sso_token')
        kwargs['barrier'] = self.barrier
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'barriers:barrier_detail',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )
