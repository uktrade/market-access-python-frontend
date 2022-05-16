from django.urls import reverse
from django.views.generic import FormView

from barriers.constants import TOP_PRIORITY_BARRIER_STATUS
from barriers.forms.edit import (
    UpdateBarrierEstimatedResolutionDateForm,
    UpdateBarrierProductForm,
    UpdateBarrierSourceForm,
    UpdateBarrierSummaryForm,
    UpdateBarrierTagsForm,
    UpdateBarrierTermForm,
    UpdateBarrierTitleForm,
    UpdateCausedByTradingBlocForm,
    UpdateCommercialValueForm,
    UpdateEconomicAssessmentEligibilityForm,
    UpdateTradeDirectionForm,
    update_barrier_priority_form_factory,
)
from users.mixins import UserMixin
from utils.context_processors import user_scope
from utils.metadata import MetadataMixin

from .mixins import APIBarrierFormViewMixin


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


class BarrierEditPriority(APIBarrierFormViewMixin, UserMixin, FormView):
    """
    Based on the user's permissions, we need to show the user a different form.

    Either one that requests/accepts a top priority status, or one that directly
    applies it.

    5 cases:
    - regular user + PB100 tag set:
        -> show form for requesting removal
    - regular user + no status:
        -> show form for rquesting PB100
    - regular user + request status:
        -> show banner
    - admin user + regular status
        -> show form for setting PB100
    - admin user + request status
        -> show form for accepting/refusing PB100
    """

    template_name = "barriers/edit/priority.html"
    # form_class = UpdateBarrierPriorityForm

    def get_context_data(self, **kwargs):
        # Add info on the user's permissions

        user = user_scope(self.request)["current_user"]
        is_user_admin = user.has_permission("set_topprioritybarrier")
        # is_user_admin = False

        REQUEST_PHASE_STATUSES = [
            TOP_PRIORITY_BARRIER_STATUS.APPROVAL_PENDING,
            TOP_PRIORITY_BARRIER_STATUS.REMOVAL_PENDING,
        ]
        is_top_priority_requested = (
            self.barrier.top_priority_status in REQUEST_PHASE_STATUSES
        )

        kwargs["user_is_top_priority_moderator"] = is_user_admin
        kwargs["is_top_priority_requested"] = is_top_priority_requested
        kwargs["is_approval_pending"] = (
            self.barrier.top_priority_status
            == TOP_PRIORITY_BARRIER_STATUS.APPROVAL_PENDING
        )
        kwargs["is_removal_pending"] = (
            self.barrier.top_priority_status
            == TOP_PRIORITY_BARRIER_STATUS.REMOVAL_PENDING
        )
        return super().get_context_data(**kwargs)

    def get_form_class(self):
        user = user_scope(self.request)["current_user"]
        is_user_admin = user.has_permission("set_topprioritybarrier")
        # is_user_admin = False
        barrier = self.barrier
        form_class = update_barrier_priority_form_factory(
            barrier=barrier, is_user_admin=is_user_admin
        )
        return form_class

    def get_initial(self):

        top_barrier_initial = "No"
        top_barrier_initial = self.barrier.top_priority_status

        return {
            "priority": self.barrier.priority["code"],
            "top_barrier": top_barrier_initial,
            "existing_tags_list": self.barrier.tags,
            "test_value": 123,
        }


class BarrierEditTerm(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/term.html"
    form_class = UpdateBarrierTermForm

    def get_initial(self):
        if self.barrier.term:
            return {"term": self.barrier.term["id"]}


class BarrierEditEstimatedResolutionDate(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/estimated_resolution_date.html"
    form_class = UpdateBarrierEstimatedResolutionDateForm

    def get_initial(self):
        return {"estimated_resolution_date": self.barrier.estimated_resolution_date}


class BarrierEditTags(UserMixin, MetadataMixin, APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/tags.html"
    form_class = UpdateBarrierTagsForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tags"] = self.metadata.get_barrier_tag_choices("edit")
        return kwargs

    def get_initial(self):
        # Check if the barrier has a Top 100 Priority barrier and set the initial value accordingly
        top_barrier_initial = "No"

        # TODO: Just here to show example of how to use perms for the PB100 tickets
        # if TOP_PRIORITY_BARRIER_EDIT_PERMISSION in self.user.permissions:
        # has perm to approve or remove top barriers

        top_barrier_initial = self.barrier.top_priority_status

        return {
            "tags": [tag["id"] for tag in self.barrier.tags],
            "top_barrier": top_barrier_initial,
        }


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


class BarrierEditCommercialValue(APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/commercial_value.html"
    form_class = UpdateCommercialValueForm

    def get_initial(self):
        return {
            "commercial_value": self.barrier.commercial_value,
            "commercial_value_explanation": self.barrier.commercial_value_explanation,
        }

    def get_success_url(self):
        return reverse(
            "barriers:assessment_detail",
            kwargs={"barrier_id": self.kwargs.get("barrier_id")},
        )


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
