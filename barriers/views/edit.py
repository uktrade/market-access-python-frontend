from django.urls import reverse
from django.views.generic import FormView

from .mixins import APIBarrierFormMixin
from barriers.forms.edit import (
    UpdateBarrierTitleForm,
    UpdateBarrierProductForm,
    UpdateBarrierDescriptionForm,
    UpdateBarrierSourceForm,
    UpdateBarrierPriorityForm,
    UpdateBarrierEUExitRelatedForm,
    UpdateBarrierProblemStatusForm,
    UpdateBarrierStatusForm,
)
from barriers.forms.statuses import BarrierStatusForm

from utils import metadata


class BarrierEditTitle(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/title.html"
    form_class = UpdateBarrierTitleForm


class BarrierEditProduct(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/product.html"
    form_class = UpdateBarrierProductForm


class BarrierEditDescription(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/description.html"
    form_class = UpdateBarrierDescriptionForm


class BarrierEditSource(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/source.html"
    form_class = UpdateBarrierSourceForm


class BarrierEditPriority(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/priority.html"
    form_class = UpdateBarrierPriorityForm


class BarrierEditEUExitRelated(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/eu_exit_related.html"
    form_class = UpdateBarrierEUExitRelatedForm


class BarrierEditProblemStatus(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/problem_status.html"
    form_class = UpdateBarrierProblemStatusForm


class BarrierEditStatus(APIBarrierFormMixin, FormView):
    template_name = "barriers/edit/status.html"
    form_class = UpdateBarrierStatusForm

    def is_barrier_resolved(self):
        return self.object.is_resolved or self.object.is_partially_resolved

    def get_initial(self):
        initial = {'status_summary': self.object.status_summary}

        if self.is_barrier_resolved():
            initial['status_date'] = self.object.status_date
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_resolved'] = self.is_barrier_resolved()
        return kwargs


class BarrierStatus(FormView):
    template_name = "barriers/status.html"
    form_class = BarrierStatusForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        form = context_data['form']
        context_data.update({
            'barrier': {'id': self.kwargs.get('barrier_id')},
            'OPEN_PENDING_ACTION': metadata.OPEN_PENDING_ACTION,
            'valid_status_values': [choice[0] for choice in form.CHOICES],
        })
        return context_data

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['token'] = self.request.session.get('sso_token')
        kwargs['id'] = self.kwargs.get('barrier_id')
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'barriers:barrier_detail',
            kwargs={'barrier_id': self.kwargs.get('barrier_id')}
        )
