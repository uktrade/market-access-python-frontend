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
            initial.update({
                'month': self.object.status_date.month,
                'year': self.object.status_date.year,
            })
        return initial

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['is_resolved'] = self.is_barrier_resolved()
        return kwargs
