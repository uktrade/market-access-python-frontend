from django.views.generic import FormView

from .mixins import APIBarrierFormViewMixin
from barriers.forms.edit import (
    UpdateBarrierTitleForm,
    UpdateBarrierProductForm,
    UpdateBarrierDescriptionForm,
    UpdateBarrierSourceForm,
    UpdateBarrierPriorityForm,
    UpdateBarrierEUExitRelatedForm,
    UpdateBarrierProblemStatusForm,
)


class BarrierEditTitle(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/title.html"
    form_class = UpdateBarrierTitleForm

    def get_initial(self):
        return {'title': self.barrier.barrier_title}


class BarrierEditProduct(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/product.html"
    form_class = UpdateBarrierProductForm

    def get_initial(self):
        return {'product': self.barrier.product}


class BarrierEditDescription(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/description.html"
    form_class = UpdateBarrierDescriptionForm

    def get_initial(self):
        return {'description': self.barrier.problem_description}


class BarrierEditSource(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/source.html"
    form_class = UpdateBarrierSourceForm

    def get_initial(self):
        return {
            'source': self.barrier.source,
            'other_source': self.barrier.other_source,
        }


class BarrierEditPriority(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/priority.html"
    form_class = UpdateBarrierPriorityForm

    def get_initial(self):
        return {'priority': self.barrier.priority['code']}


class BarrierEditEUExitRelated(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/eu_exit_related.html"
    form_class = UpdateBarrierEUExitRelatedForm

    def get_initial(self):
        return {'eu_exit_related': self.barrier.eu_exit_related}


class BarrierEditProblemStatus(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/problem_status.html"
    form_class = UpdateBarrierProblemStatusForm

    def get_initial(self):
        return {'problem_status': self.barrier.problem_status}
