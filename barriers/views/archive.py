from django.views.generic import FormView

from barriers.forms.archive import ArchiveBarrierForm
from .mixins import APIBarrierFormViewMixin


class ArchiveBarrier(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/archive.html"
    form_class = ArchiveBarrierForm
