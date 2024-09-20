from django.views.generic import TemplateView

from .mixins import BarrierMixin, RelatedBarriersContextMixin


class RelatedBarriers(RelatedBarriersContextMixin, BarrierMixin, TemplateView):
    template_name = "barriers/related_barriers.html"
