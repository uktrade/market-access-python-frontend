import logging

from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import FormView

from barriers.constants import TOP_PRIORITY_BARRIER_STATUS
from barriers.forms.edit import (
    EditBarrierPriorityForm,
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
from utils.context_processors import user_scope
from utils.metadata import MetadataMixin

from .mixins import APIBarrierFormViewMixin

logger = logging.getLogger(__name__)


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

    def get(self, request, *args, **kwargs):
        # For non-js users, if they have submitted the first question, the page reloads
        # If confirm_priority is no, then redirect to the barrier detail page.
        add_priority_confirmation = self.request.GET.get("confirm-priority", "")
        if add_priority_confirmation == "no":
            return redirect("barriers:barrier_detail", barrier_id=self.barrier.id)
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        # For non-js users, if they have submitted the first question, the page reloads
        # If yes, then confirm_priority is set to 'yes' so the frontend displays the full form.
        # We will display the full form if the barrier already has a set priority.
        # If there is an error in the submission, we also do not re-display the first question.
        add_priority_confirmation = self.request.GET.get("confirm-priority", "")
        if (
            add_priority_confirmation == "yes"
            or self.barrier.priority_level != "NONE"
            or self.request.method == "POST"
        ):
            # Reload the page and display the full priority form
            kwargs["confirm_priority"] = "yes"

        # THERE IS A BUG SURROUNDING SHOWING FORM WHEN WANTING TO REQUEST REMOVAL OF TOP 100.
        # THIS MIGHT AFFECT OTHER STATES - ADMIN LOOKING AT APPROVING FOR EXAMPLE.

        # SITUATIONS:
        # ADMIN - NO TOP 100 - WORKS - show pb100 request when country/region selected
        # ADMIN - TOP 100 APPROVAL PENDING - show admin approval/disapprove box AT ALL TIMES
        #   - DOESN'T WORK, HIDES WHEN CLICKING WATCHLIST
        # ADMIN - TOP 100 REMOVAL PENDING - show admin approval/disapprove box AT ALL TIMES
        #   - DOESN'T WORK, HIDES WHEN CLICKING WATCHLIST
        # ADMIN - TOP 100 PRIORITY BARRIER - show pb100 remove request AT ALL TIMES
        #   - DOESN'T WORK, IT HIDES WHEN CLICKING WATCHLIST AND THE 'NO' FOR REMOVAL
        # USER - NO TOP 100 - WORKS -  show pb100 request when country/region selected
        # USER - TOP 100 APPROVAL PENDING - WORKS - show pending decision AT ALL TIMES
        # USER - TOP 100 REMOVAL PENDING - WORKS - show pending decision AT ALL TIMES
        # USER - TOP 100 PRIORITY BARRIER - show pb100 remove request AT ALL TIMES
        #   - DOESN'T WORK, IT HIDES WHEN CLICKING WATCHLIST AND THE 'NO' FOR REMOVAL

        # Test locally by giving user permission to approve or reject top 100

        # Add info on the user's permissions
        user = user_scope(self.request)["current_user"]
        is_user_admin = user.has_permission("set_topprioritybarrier")

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
        barrier = self.barrier
        form_class = update_barrier_priority_form_factory(
            barrier=barrier,
            is_user_admin=is_user_admin,
            BaseFormClass=EditBarrierPriorityForm,
        )
        return form_class

    def get_initial(self):
        top_barrier_initial = (
            self.barrier.top_priority_status or TOP_PRIORITY_BARRIER_STATUS.NONE
        )

        return {
            "priority_level": self.barrier.priority_level,
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


class BarrierEditTags(MetadataMixin, APIBarrierFormViewMixin, FormView):
    template_name = "barriers/edit/tags.html"
    form_class = UpdateBarrierTagsForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["tags"] = self.metadata.get_barrier_tag_choices("edit")
        return kwargs

    def get_initial(self):
        top_barrier_initial = (
            self.barrier.top_priority_status or TOP_PRIORITY_BARRIER_STATUS.NONE
        )

        return {
            "tags": [tag["id"] for tag in self.barrier.tags],
            "top_barrier": top_barrier_initial,
        }

    def get_context_data(self, **kwargs):
        # Add info on the user's permissions

        user = user_scope(self.request)["current_user"]
        is_user_admin = user.has_permission("set_topprioritybarrier")

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
        barrier = self.barrier
        form_class = update_barrier_priority_form_factory(
            barrier=barrier,
            is_user_admin=is_user_admin,
            BaseFormClass=UpdateBarrierTagsForm,
        )
        return form_class


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
