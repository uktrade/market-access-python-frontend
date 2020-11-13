from django.views.generic import FormView
from django.urls import reverse

from .mixins import APIBarrierFormViewMixin
from barriers.forms.edit import (
    UpdateBarrierEndDateForm,
    UpdateBarrierTitleForm,
    UpdateBarrierProductForm,
    UpdateBarrierSourceForm,
    UpdateBarrierSummaryForm,
    UpdateBarrierPriorityForm,
    UpdateBarrierTagsForm,
    UpdateBarrierTermForm,
    UpdateCausedByTradingBlocForm,
    UpdateEconomicAssessmentEligibilityForm,
    UpdateTradeDirectionForm,
)
from utils.metadata import MetadataMixin


class BarrierEditTitle(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/title.html"
    form_class = UpdateBarrierTitleForm

    def get_initial(self):
        return {"title": self.barrier.title}


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
        if self.barrier.source:
            return {
                "source": self.barrier.source.get("code"),
                "other_source": self.barrier.other_source,
            }


class BarrierEditPriority(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/priority.html"
    form_class = UpdateBarrierPriorityForm

    def get_initial(self):
        return {"priority": self.barrier.priority["code"]}


class BarrierEditTerm(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/term.html"
    form_class = UpdateBarrierTermForm

    def get_initial(self):
        if self.barrier.term:
            return {"term": self.barrier.term["id"]}


class BarrierEditEndDate(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/end_date.html"
    form_class = UpdateBarrierEndDateForm

    def get_initial(self):
        return {"end_date": self.barrier.end_date}


class BarrierEditTags(MetadataMixin, APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/tags.html"
    form_class = UpdateBarrierTagsForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tags"] = self.metadata.get_barrier_tag_choices()
        return kwargs

    def get_initial(self):
        return {"tags": [tag["id"] for tag in self.barrier.tags]}


class BarrierEditTradeDirection(MetadataMixin, APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/trade_direction.html"
    form_class = UpdateTradeDirectionForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["trade_direction_choices"] = self.metadata.get_trade_direction_choices()
        return kwargs

    def get_initial(self):
        if self.barrier.trade_direction:
            return {"trade_direction": str(self.barrier.trade_direction["id"])}


class BarrierEditCausedByTradingBloc(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/caused_by_trading_bloc.html"
    form_class = UpdateCausedByTradingBlocForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["trading_bloc"] = self.barrier.country.get("trading_bloc")
        return kwargs

    def get_initial(self):
        return {"caused_by_trading_bloc": self.barrier.caused_by_trading_bloc}


class BarrierEditEconomicAssessmentEligibility(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/economic_assessment_eligibility.html"
    form_class = UpdateEconomicAssessmentEligibilityForm

    def get_initial(self):
        return {
            "economic_assessment_eligibility": self.barrier.economic_assessment_eligibility,
            "economic_assessment_eligibility_summary": self.barrier.economic_assessment_eligibility_summary,
        }

    def get_success_url(self):
        return reverse(
            "barriers:assessment_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )
