from django.views.generic import FormView

from barriers.forms.archive import ArchiveBarrierForm, UnarchiveBarrierForm
from .mixins import APIBarrierFormViewMixin


class ArchiveBarrier(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/archive.html"
    form_class = ArchiveBarrierForm


class UnarchiveBarrier(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/unarchive.html"
    form_class = UnarchiveBarrierForm
