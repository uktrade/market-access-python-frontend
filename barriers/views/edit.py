import logging

from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView

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
from utils.api.client import MarketAccessAPIClient
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
            user = user_scope(self.request)["current_user"]
            is_user_admin = user.has_permission("set_topprioritybarrier")
            # if the user is admin remove all priorities
            rejection_reason = self.request.GET.get("rejection-reason", "")
            self.remove_all_priorities(
                is_admin=is_user_admin, rejection_reason=rejection_reason
            )
            return redirect("barriers:barrier_detail", barrier_id=self.barrier.id)

            return super().get(request, *args, **kwargs)
        else:
            return super().get(request, *args, **kwargs)

    def remove_all_priorities(self, is_admin=False, rejection_reason=""):
        # Remove all priority tags
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        if is_admin:
            client.barriers.patch(
                self.barrier.id, priority_level="NONE", top_priority_status="NONE"
            )
        else:
            if self.barrier.top_priority_status == "APPROVED":
                client.barriers.patch(
                    self.barrier.id,
                    priority_level="NONE",
                    top_priority_status="REMOVAL_PENDING",
                    rejection_reason=rejection_reason,
                )
            else:
                client.barriers.patch(
                    self.barrier.id,
                    priority_level="NONE",
                )

    def get_context_data(self, **kwargs):

        # For non-js users, if they have submitted the first question, the page reloads
        # If yes, then confirm_priority is set to 'yes' so the frontend displays the full form.
        # We will display the full form if the barrier already has a set priority.
        # If there is an error in the submission, we also do not re-display the first question.
        add_priority_confirmation = self.request.GET.get("confirm-priority", "")
        kwargs["confirm_priority"] = add_priority_confirmation
        # Add info on the user's permissions
        user = user_scope(self.request)["current_user"]
        is_user_admin = user.has_permission("set_topprioritybarrier")
        kwargs["is_user_admin"] = is_user_admin

        REQUEST_PHASE_STATUSES = [
            TOP_PRIORITY_BARRIER_STATUS.APPROVAL_PENDING,
            TOP_PRIORITY_BARRIER_STATUS.REMOVAL_PENDING,
        ]
        is_top_priority_requested = (
            self.barrier.top_priority_status in REQUEST_PHASE_STATUSES
        )

        kwargs["user_is_top_priority_moderator"] = is_user_admin
        kwargs["is_top_priority_requested"] = is_top_priority_requested
        kwargs["top_priority_status"] = self.barrier.top_priority_status
        kwargs["is_top_priority"] = (
            self.barrier.top_priority_status == TOP_PRIORITY_BARRIER_STATUS.APPROVED
        )
        kwargs["is_approval_pending"] = (
            self.barrier.top_priority_status
            == TOP_PRIORITY_BARRIER_STATUS.APPROVAL_PENDING
        )
        kwargs["is_removal_pending"] = (
            self.barrier.top_priority_status
            == TOP_PRIORITY_BARRIER_STATUS.REMOVAL_PENDING
        )

        # Get an existing priority summary to allow for editing if pending approval
        if self.barrier.top_priority_status in [
            TOP_PRIORITY_BARRIER_STATUS.APPROVAL_PENDING,
            TOP_PRIORITY_BARRIER_STATUS.REMOVAL_PENDING,
            TOP_PRIORITY_BARRIER_STATUS.APPROVED,
        ]:
            client = MarketAccessAPIClient(self.request.session.get("sso_token"))
            existing_top_priority_summary = client.barriers.get_top_priority_summary(
                barrier=self.barrier.id
            )
            if existing_top_priority_summary["top_priority_summary_text"]:
                kwargs["existing_top_priority_summary"] = existing_top_priority_summary[
                    "top_priority_summary_text"
                ]
                kwargs["created_by"] = existing_top_priority_summary["created_by"]
                kwargs["created_on"] = existing_top_priority_summary["created_on"]
                kwargs["modified_by"] = existing_top_priority_summary["modified_by"]
                kwargs["modified_on"] = existing_top_priority_summary["modified_on"]

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

    def get_success_url(self):
        if self.form.requested_change:
            return reverse_lazy(
                "barriers:edit_estimated_resolution_date_confirmation_page",
                kwargs={"barrier_id": self.kwargs.get("barrier_id")},
            )
        else:
            return reverse_lazy(
                "barriers:barrier_detail",
                kwargs={"barrier_id": self.kwargs.get("barrier_id")},
            )

    def form_valid(self, form):
        self.form = form
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["barrier"] = self.barrier
        context["current_user"] = user_scope(self.request)["current_user"]
        return context

    def get_initial(self):
        initial = super().get_initial()
        if self.barrier.proposed_estimated_resolution_date:
            proposed_date = self.barrier.proposed_estimated_resolution_date
        else:
            proposed_date = self.barrier.estimated_resolution_date
        if self.barrier.estimated_resolution_date_change_reason:
            proposed_reason = self.barrier.estimated_resolution_date_change_reason
        else:
            proposed_reason = None

        return {
            "estimated_resolution_date": proposed_date,
            "estimated_resolution_date_change_reason": proposed_reason,
        }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        kwargs["barrier_id"] = self.kwargs.get("barrier_id")
        kwargs["user"] = user_scope(self.request)["current_user"]

        return kwargs


class BarrierEditEstimatedResolutionDateConfirmationPage(TemplateView):
    template_name = "barriers/edit/estimated_resolution_date_confirmation_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        barrier_id = kwargs.get("barrier_id")
        kwargs["token"] = self.request.session.get("sso_token")
        client = MarketAccessAPIClient(kwargs["token"])
        barrier = client.barriers.get(id=barrier_id)
        context["barrier"] = barrier
        return context

    # def get(self, request, *args, **kwargs):
    #     barrier_id = kwargs.get("barrier_id")
    #     kwargs["token"] = self.request.session.get("sso_token")
    #     client = MarketAccessAPIClient(kwargs["token"])
    #     barrier = client.barriers.get(id=barrier_id)
    #     return render(request, self.template_name, {"barrier": barrier})


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
