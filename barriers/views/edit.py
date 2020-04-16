from django.views.generic import FormView

from .mixins import APIBarrierFormViewMixin
from barriers.forms.edit import (
    UpdateBarrierEndDateForm,
    UpdateBarrierTitleForm,
    UpdateBarrierProductForm,
    UpdateBarrierSourceForm,
    UpdateBarrierSummaryForm,
    UpdateBarrierPriorityForm,
    UpdateBarrierProblemStatusForm,
    UpdateBarrierTagsForm,
)
from utils.metadata import get_metadata


class BarrierEditTitle(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/title.html"
    form_class = UpdateBarrierTitleForm

    def get_initial(self):
        return {"title": self.barrier.barrier_title}


class BarrierEditProduct(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/product.html"
    form_class = UpdateBarrierProductForm

    def get_initial(self):
        return {"product": self.barrier.product}


class BarrierEditSummary(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/summary.html"
    form_class = UpdateBarrierSummaryForm

    def get_initial(self):
        return {
            "summary": self.barrier.summary,
            "is_summary_sensitive": self.barrier.is_summary_sensitive,
        }


class BarrierEditSource(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/source.html"
    form_class = UpdateBarrierSourceForm

    def get_initial(self):
        return {
            "source": self.barrier.source,
            "other_source": self.barrier.other_source,
        }


class BarrierEditPriority(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/priority.html"
    form_class = UpdateBarrierPriorityForm

    def get_initial(self):
        return {"priority": self.barrier.priority["code"]}


class BarrierEditProblemStatus(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/problem_status.html"
    form_class = UpdateBarrierProblemStatusForm

    def get_initial(self):
        return {"problem_status": self.barrier.problem_status}


class BarrierEditEndDate(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/end_date.html"
    form_class = UpdateBarrierEndDateForm

    def get_initial(self):
        return {"end_date": self.barrier.end_date}


class BarrierEditTags(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/tags.html"
    form_class = UpdateBarrierTagsForm
    metadata = get_metadata()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tags"] = self.metadata.get_barrier_tag_choices()
        return kwargs

    def get_initial(self):
        return {"tags": [tag["id"] for tag in self.barrier.tags]}
