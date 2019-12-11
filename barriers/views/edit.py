from django.views.generic import FormView

from .mixins import APIBarrierFormMixin
from barriers.forms import (
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
