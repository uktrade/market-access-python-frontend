import logging

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MaxLengthValidator
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from barriers.constants import (
    DEPRECATED_TAGS,
    TOP_PRIORITY_BARRIER_STATUS,
    TOP_PRIORITY_BARRIER_STATUS_APPROVAL_CHOICES,
    TOP_PRIORITY_BARRIER_STATUS_APPROVE_REMOVAL_CHOICES,
    TOP_PRIORITY_BARRIER_STATUS_APPROVE_REQUEST_CHOICES,
    TOP_PRIORITY_BARRIER_STATUS_REQUEST_APPROVAL_CHOICES,
    TOP_PRIORITY_BARRIER_STATUS_REQUEST_REMOVAL_CHOICES,
    TOP_PRIORITY_BARRIER_STATUS_RESOLVED_CHOICES,
)
from utils.api.client import MarketAccessAPIClient
from utils.forms.fields import (
    MonthYearInFutureField,
    MultipleChoiceFieldWithHelpText,
    TrueFalseBooleanField,
    YesNoBooleanField,
    YesNoDontKnowBooleanField,
)
from utils.forms.mixins import ClearableMixin

from .mixins import APIFormMixin, EstimatedResolutionDateApprovalMixin

logger = logging.getLogger(__name__)


class UpdateCommercialValueForm(APIFormMixin, forms.Form):
    commercial_value = forms.IntegerField(
        min_value=0,
        max_value=1000000000000,
        localize=True,
        label="What is the value of the barrier to affected businesses?",
        error_messages={
            "required": "Enter the value of the barrier",
            "min_value": "Value must be 0 or more",
            "max_value": "Value must be 1000000000000 or less",
            "invalid": "Enter a whole number",
        },
    )
    commercial_value_explanation = forms.CharField(
        widget=forms.Textarea,
        error_messages={"required": "Enter details of the estimated value"},
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(id=self.id, **self.cleaned_data)


class UpdateBarrierTitleForm(APIFormMixin, forms.Form):
    title = forms.CharField(
        label="Suggest a title for this barrier",
        help_text=(
            "Include both the title or service name and the country being "
            "exported to, for example, Import quotas for steel rods in India."
        ),
        max_length=255,
        error_messages={
            "max_length": "Title should be %(limit_value)d characters or fewer",
            "required": "Enter a title for this barrier",
        },
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(id=self.id, title=self.cleaned_data["title"])


class UpdateBarrierProductForm(APIFormMixin, forms.Form):
    product = forms.CharField(
        label="What product or service is being exported?",
        max_length=255,
        error_messages={
            "max_length": (
                "Product or service should be %(limit_value)d characters or fewer"
            ),
            "required": "Enter a product or service",
        },
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(id=self.id, product=self.cleaned_data["product"])


class UpdateBarrierSummaryForm(APIFormMixin, forms.Form):
    summary = forms.CharField(
        label="Description",
        widget=forms.Textarea,
        error_messages={"required": "Enter a brief description for this barrier"},
        help_text=(
            "This description will only be used internally."
            "Explain how the barrier is affecting trade, and why it exists"
            "Where relevant include the specific laws or measures blocking trade, and any political context."
        ),
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            summary=self.cleaned_data["summary"],
        )


class ProgressUpdateForm(
    ClearableMixin, EstimatedResolutionDateApprovalMixin, APIFormMixin, forms.Form
):
    CHOICES = [
        (
            "ON_TRACK",
            mark_safe(
                "<span class='govuk-body'>On Track</span> <span class='govuk-hint'>Barrier will be resolved"
                " in the target financial year</span>"
            ),
        ),
        (
            "RISK_OF_DELAY",
            mark_safe(
                "<span class='govuk-body'>Risk of delay</span> <span class='govuk-hint'>Barrier might not be"
                " resolved in the target financial year</span>"
            ),
        ),
        (
            "DELAYED",
            mark_safe(
                "<span class='govuk-body'>Delayed</span> <span class='govuk-hint'>Barrier will not be"
                " resolved in the target financial year</span>"
            ),
        ),
    ]
    status = forms.ChoiceField(
        label="Delivery confidence",
        choices=CHOICES,
        widget=forms.RadioSelect,
        error_messages={
            "required": "Select if delivery is on track, at risk of delay or delayed"
        },
    )
    update = forms.CharField(
        label="Current status",
        widget=forms.Textarea,
        required=False,
    )
    update_1 = forms.CharField(
        label="Explain why barrier resolution is on track",
        widget=forms.Textarea,
        error_messages={"missing_update": "missing update"},
        required=False,
    )

    update_2 = forms.CharField(
        label="Explain why there is a risk that barrier resolution may be delayed",
        widget=forms.Textarea,
        required=False,
    )

    update_3 = forms.CharField(
        label="Explain why barrier resolution is delayed",
        widget=forms.Textarea,
        required=False,
    )

    estimated_resolution_date = MonthYearInFutureField(
        label="Estimated resolution date (optional)",
        help_text=(
            "You can change the estimated resolution date as part of this update."
            " The date should be no more than 5 years in the future. Enter the date in the format, 11 2024."
        ),
        error_messages={
            "invalid_year": "Enter an estimated resolution date",
            "invalid_month": "Enter an estimated resolution date",
        },
        required=False,
    )
    estimated_resolution_date_change_reason = forms.CharField(
        label="What has caused the change in estimated resolution date?",
        widget=forms.Textarea,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.barrier_id = kwargs.get("barrier_id")
        self.progress_update_id = kwargs.get("progress_update_id")
        self.user = kwargs.get("user")

    def clean_estimated_resolution_date(self):
        if self.cleaned_data["estimated_resolution_date"]:
            return self.cleaned_data["estimated_resolution_date"].isoformat()
        return self.cleaned_data["estimated_resolution_date"]

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        update_1 = cleaned_data.get("update_1")
        update_2 = cleaned_data.get("update_2")
        update_3 = cleaned_data.get("update_3")

        if status == "ON_TRACK":
            if update_1:
                self.message = update_1
                self.update = update_1
            else:
                self.add_error(
                    "update_1",
                    ValidationError(
                        _("Enter detail about your delivery confidence"),
                        code="missing_update",
                    ),
                )
        elif status == "RISK_OF_DELAY":
            if update_2:
                self.message = update_2
                self.update = update_2
            else:
                self.add_error(
                    "update_2",
                    ValidationError(
                        _("Enter detail about your delivery confidence"),
                        code="missing_update",
                    ),
                )
        if status == "DELAYED":
            if update_3:
                self.message = update_3
                self.update = update_3
            else:
                self.add_error(
                    "update_3",
                    ValidationError(
                        _("Enter detail about your delivery confidence"),
                        code="missing_update",
                    ),
                )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.progress_update_id:
            client.barriers.patch_top_100_progress_update(
                barrier=self.barrier_id,
                id=self.progress_update_id,
                status=self.cleaned_data["status"],
                message=self.message,
            )
        else:
            client.barriers.create_top_100_progress_update(
                barrier=self.barrier_id,
                status=self.cleaned_data["status"],
                message=self.message,
            )

        estimated_resolution_date = self.cleaned_data.get("estimated_resolution_date")
        is_future_date = self.does_new_estimated_date_require_approval(
            self.cleaned_data
        )

        if (not self.is_user_admin) and (is_future_date):
            self.requested_change = True
            client.barriers.patch(
                id=str(self.barrier_id),
                proposed_estimated_resolution_date=estimated_resolution_date,
                estimated_resolution_date_change_reason=self.cleaned_data.get(
                    "estimated_resolution_date_change_reason"
                ),
            )
        else:
            self.requested_change = False
            client.barriers.patch(
                id=str(self.barrier_id),
                estimated_resolution_date=estimated_resolution_date,
                proposed_estimated_resolution_date=estimated_resolution_date,
                estimated_resolution_date_change_reason=self.cleaned_data.get(
                    "estimated_resolution_date_change_reason", ""
                ),
            )


class ProgrammeFundProgressUpdateForm(
    EstimatedResolutionDateApprovalMixin, APIFormMixin, forms.Form
):
    milestones_and_deliverables = forms.CharField(
        label="Milestones and deliverables",
        widget=forms.Textarea,
        error_messages={
            "required": "Enter your milestones and deliverables",
        },
    )
    expenditure = forms.CharField(
        label="Expenditure",
        widget=forms.Textarea,
        error_messages={"required": "Enter your expenditure"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.barrier_id = kwargs.get("barrier_id")
        self.programme_fund_update_id = kwargs.get("progress_update_id", None)
        self.user = kwargs.get("user", None)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if hasattr(self, "programme_fund_update_id"):
            client.barriers.patch_programme_fund_progress_update(
                barrier=self.barrier_id,
                id=self.programme_fund_update_id,
                milestones_and_deliverables=self.cleaned_data[
                    "milestones_and_deliverables"
                ],
                expenditure=self.cleaned_data["expenditure"],
            )
        else:
            client.barriers.create_programme_fund_progress_update(
                barrier=self.barrier_id,
                milestones_and_deliverables=self.cleaned_data[
                    "milestones_and_deliverables"
                ],
                expenditure=self.cleaned_data["expenditure"],
            )


class EditBarrierPriorityForm(APIFormMixin, forms.Form):
    top_priority_help_text = (
        "Barrier needs significant input from DBT policy teams, other "
        "government departments or regulators to resolve."
    )
    overseas_help_text = (
        "Barrier can be resolved by officials at Post, with no or limited support needed from policy teams "
        "in London departments. "
    )
    watchlist_help_text = "Of potential interest but not actively being worked on."
    CHOICES = [
        (
            "PB100",
            "<span class='govuk-body'>Top 100 priority barrier</span> <span"
            f" class='govuk-hint'>{top_priority_help_text}</span>",
        ),
        (
            "OVERSEAS",
            "<span class='govuk-body'>Overseas delivery</span> <span"
            f" class='govuk-hint'>{overseas_help_text}</span>",
        ),
        (
            "WATCHLIST",
            "<span class='govuk-body'>Watch list</span> <span"
            f" class='govuk-hint'>{watchlist_help_text}</span>",
        ),
    ]
    priority_level = forms.ChoiceField(
        label="Which priority type is most relevant to you and your team?",
        choices=CHOICES,
        widget=forms.RadioSelect,
        error_messages={"required": "Select a priority type"},
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)

        # PB100 setting does not go into priority_level field, it is recorded seperately
        if self.cleaned_data["priority_level"] == "PB100":
            self.cleaned_data["priority_level"] = "NONE"

        patch_args = {
            "id": self.id,
            "priority_level": self.cleaned_data["priority_level"],
        }

        existing_top_priority_status = getattr(
            client.barriers.get(id=self.id), "top_priority_status"
        )

        # If no answer received, set default to the existing status
        # Otherwise, use the input
        if self.fields.get("top_barrier"):
            if self.cleaned_data["top_barrier"] == "":
                patch_args["top_priority_status"] = existing_top_priority_status
            else:
                patch_args["top_priority_status"] = self.cleaned_data["top_barrier"]

        # Set additional args depending on if questions are answered
        if self.fields.get("top_priority_rejection_summary"):
            patch_args["top_priority_rejection_summary"] = self.cleaned_data[
                "top_priority_rejection_summary"
            ]

        # Update the priority summary if it is present/amended
        if self.fields.get("priority_summary"):
            submitted_summary = self.cleaned_data["priority_summary"]
            existing_top_priority_summary = client.barriers.get_top_priority_summary(
                barrier=self.id
            )
            summary_patch_args = {
                "top_priority_summary": {
                    "top_priority_summary_text": submitted_summary,
                    "barrier": self.id,
                }
            }

            # Patch if the existing summary has a creation date, otherwise create new
            if submitted_summary:
                if existing_top_priority_summary["top_priority_summary_text"]:
                    if (
                        existing_top_priority_summary["top_priority_summary_text"]
                        != submitted_summary
                    ):
                        client.barriers.patch_top_priority_summary(
                            **summary_patch_args["top_priority_summary"]
                        )
                else:
                    client.barriers.create_top_priority_summary(
                        **summary_patch_args["top_priority_summary"]
                    )

        client.barriers.patch(**patch_args)


class UpdateBarrierTagsForm(APIFormMixin, forms.Form):
    tags = MultipleChoiceFieldWithHelpText(
        label="Is this issue caused by or related to any of the following?",
        choices=[],
        required=False,
    )

    def __init__(self, tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tags"].choices = tags
        self.deprecated_tags = DEPRECATED_TAGS

    def save(self):
        client = MarketAccessAPIClient(self.token)

        patch_args = {
            "id": self.id,
            "tags": self.cleaned_data["tags"],
        }

        client.barriers.patch(**patch_args)


def update_barrier_priority_form_factory(
    barrier, is_user_admin=False, BaseFormClass=EditBarrierPriorityForm
):
    """
    type: (Barrier, bool) -> EditBarrierPriorityForm

    Return a form for updating the priority of a barrier based on
    a barrier's Top priority status and if the user has moderator permissions.

    Should support 5 cases:
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
    top_barrier_status_field_label = "Should this be a top 100 priority barrier?"
    top_barrier_status_field_choices = (
        TOP_PRIORITY_BARRIER_STATUS_REQUEST_APPROVAL_CHOICES
    )

    REQUEST_PHASE_STATUSES = [
        TOP_PRIORITY_BARRIER_STATUS.APPROVAL_PENDING,
        TOP_PRIORITY_BARRIER_STATUS.REMOVAL_PENDING,
    ]

    is_top_priority_in_request_phase = (
        barrier.top_priority_status in REQUEST_PHASE_STATUSES
    )

    show_reason_for_rejection_field = False
    show_reason_for_top_priority_field = True
    show_top_priority_status_field = True
    if is_user_admin:
        top_barrier_status_field_choices = TOP_PRIORITY_BARRIER_STATUS_APPROVAL_CHOICES
        if barrier.top_priority_status == TOP_PRIORITY_BARRIER_STATUS.APPROVAL_PENDING:
            # user needs to approve/deny the request
            top_barrier_status_field_label = (
                "This barrier has been tagged as a Top 100 priority barrier. Do you"
                " agree with this status?"
            )
            top_barrier_status_field_choices = (
                TOP_PRIORITY_BARRIER_STATUS_APPROVE_REQUEST_CHOICES
            )
            show_reason_for_rejection_field = True
            show_reason_for_top_priority_field = False
        elif barrier.top_priority_status == TOP_PRIORITY_BARRIER_STATUS.REMOVAL_PENDING:
            # user needs to approve/deny the request
            top_barrier_status_field_label = (
                "This barrier has been requested to be removed as a Top 100 priority"
                " barrier.  Do you agree with this status?"
            )
            top_barrier_status_field_choices = (
                TOP_PRIORITY_BARRIER_STATUS_APPROVE_REMOVAL_CHOICES
            )
            show_reason_for_rejection_field = True
            show_reason_for_top_priority_field = False
        elif barrier.top_priority_status == TOP_PRIORITY_BARRIER_STATUS.RESOLVED:
            top_barrier_status_field_choices = (
                TOP_PRIORITY_BARRIER_STATUS_RESOLVED_CHOICES
            )
    else:
        # regular user
        if is_top_priority_in_request_phase:
            show_reason_for_top_priority_field = True
            show_top_priority_status_field = False
        elif barrier.top_priority_status == TOP_PRIORITY_BARRIER_STATUS.NONE:
            top_barrier_status_field_choices = (
                TOP_PRIORITY_BARRIER_STATUS_REQUEST_APPROVAL_CHOICES
            )
        elif barrier.top_priority_status == TOP_PRIORITY_BARRIER_STATUS.RESOLVED:
            top_barrier_status_field_choices = (
                TOP_PRIORITY_BARRIER_STATUS_RESOLVED_CHOICES
            )
        else:
            top_barrier_status_field_choices = (
                TOP_PRIORITY_BARRIER_STATUS_REQUEST_REMOVAL_CHOICES
            )

    class CustomizedUpdateBarrierPriorityForm(BaseFormClass):
        if show_top_priority_status_field:
            top_barrier = forms.ChoiceField(
                label=top_barrier_status_field_label,
                help_text=(
                    "This is the government's global list of priority market access"
                    " barriers."
                ),
                choices=top_barrier_status_field_choices,
                widget=forms.RadioSelect,
                required=False,
            )

        if show_reason_for_top_priority_field:
            label_text = "Describe why this should be a top 100 priority barrier"
            label_hint = (
                "Provide the barrier's economic value with any supporting data,"
                " strategic importance, and estimated resolution month and year."
            )

            # If barrier is already top priority, change the labeling to reflect removal request
            if barrier.top_priority_status == TOP_PRIORITY_BARRIER_STATUS.APPROVED:
                label_text = (
                    "Describe why this should be removed as a top 100 priority barrier"
                )
                label_hint = ""

            priority_summary = forms.CharField(
                label=label_text,
                help_text=label_hint,
                widget=forms.Textarea,
                required=False,
            )
        if show_reason_for_rejection_field:
            top_priority_rejection_summary = forms.CharField(
                label=(
                    "Please state your reason for rejecting the barrier change request"
                ),
                widget=forms.Textarea,
                required=False,
            )

        def clean_priority_summary(self):
            cleaned_priority_summary = self.cleaned_data["priority_summary"]
            if cleaned_priority_summary:
                # The field is filled in so we can ignore any checks
                return cleaned_priority_summary

            # The field is empty
            # If the user changed the top_priority_status of the barrrier
            # we should raise a ValidationError

            cleaned_top_priority_status = self.cleaned_data.get("top_barrier")

            # If top priority not given, return as we don't need to continue
            if cleaned_top_priority_status is None:
                return ""

            has_top_priority_status_changed = (
                cleaned_top_priority_status != barrier.top_priority_status
            )
            if has_top_priority_status_changed:
                raise forms.ValidationError("Enter a description")
            return cleaned_priority_summary

        def clean_top_priority_rejection_summary(self):
            rejection_summary = self.cleaned_data["top_priority_rejection_summary"]
            if rejection_summary:
                # rejection summary has been filled is, so no need to check
                return rejection_summary

            # we need to raise a ValidationError if the admin rejected a request
            # but did not supply a rejection summary
            admins_decision = self.cleaned_data.get("top_barrier")
            if (
                barrier.top_priority_status
                == TOP_PRIORITY_BARRIER_STATUS.REMOVAL_PENDING
            ):
                if admins_decision == TOP_PRIORITY_BARRIER_STATUS.APPROVED:
                    raise forms.ValidationError(
                        "A reason needs to be provided if the removal request is"
                        " rejected"
                    )
            elif (
                barrier.top_priority_status
                == TOP_PRIORITY_BARRIER_STATUS.APPROVAL_PENDING
            ):
                if admins_decision == TOP_PRIORITY_BARRIER_STATUS.NONE:
                    raise forms.ValidationError(
                        "A reason needs to be provided if the request is rejected"
                    )

            return rejection_summary

    return CustomizedUpdateBarrierPriorityForm


class UpdateBarrierEstimatedResolutionDateForm(
    EstimatedResolutionDateApprovalMixin, ClearableMixin, APIFormMixin, forms.Form
):
    estimated_resolution_date = MonthYearInFutureField(
        label="Estimated resolution date",
        help_text="The date should be no more than 5 years in the future. Enter the date in the format, 11 2024.",
        error_messages={"required": "Enter an estimated resolution date"},
    )
    estimated_resolution_date_change_reason = forms.CharField(
        label="What has caused the change in estimated resolution date?",
        widget=forms.Textarea,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)

        estimated_resolution_date = self.cleaned_data.get("estimated_resolution_date")
        is_future_date = self.does_new_estimated_date_require_approval(
            self.cleaned_data
        )

        if (not self.is_user_admin) and (is_future_date):
            self.requested_change = True
            client.barriers.patch(
                id=str(self.barrier_id),
                proposed_estimated_resolution_date=estimated_resolution_date,
                estimated_resolution_date_change_reason=self.cleaned_data.get(
                    "estimated_resolution_date_change_reason"
                ),
            )
        else:
            self.requested_change = False
            client.barriers.patch(
                id=str(self.barrier_id),
                estimated_resolution_date=estimated_resolution_date,
                proposed_estimated_resolution_date=estimated_resolution_date,
                estimated_resolution_date_change_reason=self.cleaned_data.get(
                    "estimated_resolution_date_change_reason", ""
                ),
            )


class UpdateTradeDirectionForm(APIFormMixin, forms.Form):
    trade_direction = forms.ChoiceField(
        label="Which trade direction does this barrier affect?",
        choices=[],
        widget=forms.RadioSelect,
        error_messages={"required": "Select a trade direction"},
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id, trade_direction=self.cleaned_data["trade_direction"]
        )

    def __init__(self, trade_direction_choices, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["trade_direction"].choices = trade_direction_choices


class CausedByTradingBlocForm(forms.Form):
    caused_by_trading_bloc = YesNoDontKnowBooleanField(
        label="",
        error_messages={
            "required": "Indicate if the barrier was caused by the trading bloc"
        },
    )

    def __init__(self, trading_bloc=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if trading_bloc:
            # add custom labels and help_text only when provided
            self.fields["caused_by_trading_bloc"].label = (
                "Was this barrier caused by a regulation introduced by "
                f"{trading_bloc['short_name']}?"
            )
            self.fields["caused_by_trading_bloc"].help_text = self.get_help_text(
                trading_bloc.get("code")
            )

    def get_help_text(self, trading_bloc_code):
        help_text = {
            "TB00016": (
                "Yes should be selected if the barrier is a local application of an EU "
                "regulation. If it is an EU-wide barrier, the country location should "
                "be changed to EU in the location screen."
            ),
            "TB00026": (
                "Yes should be selected if the barrier is a local application of an"
                " Mercosur regulation. If it is an Mercosur-wide barrier, the country"
                " location should be changed to Southern Common Market (Mercosur) in"
                " the location screen."
            ),
            "TB00013": (
                "Yes should be selected if the barrier is a local application of an"
                " EAEU regulation. If it is an EAEU-wide barrier, the country location"
                " should be changed to Eurasian Economic Union (EAEU) in the location"
                " screen."
            ),
            "TB00017": (
                "Yes should be selected if the barrier is a local application of an GCC"
                " regulation. If it is an GCC-wide barrier, the country location should"
                " be changed to Gulf Cooperation Council (GCC) in the location screen."
            ),
        }
        return help_text.get(trading_bloc_code, "")


class UpdateCausedByTradingBlocForm(APIFormMixin, CausedByTradingBlocForm):
    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            caused_by_trading_bloc=self.cleaned_data["caused_by_trading_bloc"],
        )


class UpdateEconomicAssessmentEligibilityForm(APIFormMixin, forms.Form):
    economic_assessment_eligibility = YesNoBooleanField(
        label="Is the barrier eligible for an initial economic assessment?",
        error_messages={"required": "Select yes or no"},
    )
    economic_assessment_eligibility_summary = forms.CharField(
        label="Provide the reason this barrier is not eligible",
        max_length=1500,
        widget=forms.Textarea,
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        economic_assessment_eligibility = cleaned_data.get(
            "economic_assessment_eligibility"
        )
        economic_assessment_eligibility_summary = cleaned_data.get(
            "economic_assessment_eligibility_summary"
        )

        if economic_assessment_eligibility is False:
            if not economic_assessment_eligibility_summary:
                self.add_error(
                    "economic_assessment_eligibility_summary",
                    "Enter the reason this barrier is not eligible",
                )
        else:
            cleaned_data["economic_assessment_eligibility_summary"] = ""

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            economic_assessment_eligibility=self.cleaned_data[
                "economic_assessment_eligibility"
            ],
            economic_assessment_eligibility_summary=self.cleaned_data[
                "economic_assessment_eligibility_summary"
            ],
        )


class NextStepsItemForm(APIFormMixin, forms.Form):
    NEXT_STEPS_ITEMS_STATUS_CHOICES = [
        ("IN_PROGRESS", "In progress"),
        ("COMPLETED", "Completed"),
    ]

    status = forms.ChoiceField(
        label="Status",
        choices=NEXT_STEPS_ITEMS_STATUS_CHOICES,
        widget=forms.RadioSelect,
        error_messages={"required": "Select the current status of this item"},
    )

    next_step_item = forms.CharField(
        label="What is the activity?",
        # help_text=("What are the action being taken"),
        widget=forms.Textarea,
        error_messages={"required": "Enter an activity"},
        required=True,
        validators=[MaxLengthValidator(150)],
    )

    next_step_owner = forms.CharField(
        label="Who's doing the activity?",
        # help_text=("Who will be responsible for completing this item"),
        widget=forms.Textarea,
        error_messages={"required": "Enter who's doing the activity"},
        required=True,
        validators=[MaxLengthValidator(150)],
    )

    completion_date = MonthYearInFutureField(
        label="When will the activity be completed?",
        # help_text=("Add the target date for the completion of this item"),
        error_messages={
            "required": "Enter when the activity will be completed",
            "invalid_year": "Enter a completion date",
            "invalid_month": "Enter a completion date",
        },
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super(NextStepsItemForm, self).__init__(*args, **kwargs)
        self.barrier_id = kwargs.get("barrier_id")
        self.item_id = kwargs.get("item_id")
        self.user = kwargs.get("user")

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.item_id:
            client.barriers.patch_next_steps_item(
                barrier=self.barrier_id,
                id=self.item_id,
                status=self.cleaned_data["status"],
                next_step_owner=self.cleaned_data["next_step_owner"],
                next_step_item=self.cleaned_data["next_step_item"],
                completion_date=self.cleaned_data["completion_date"],
            )
        else:
            client.barriers.create_next_steps_item(
                barrier=self.barrier_id,
                status=self.cleaned_data["status"],
                next_step_owner=self.cleaned_data["next_step_owner"],
                next_step_item=self.cleaned_data["next_step_item"],
                completion_date=self.cleaned_data["completion_date"],
            )


class UpdateBarrierStartDateForm(ClearableMixin, APIFormMixin, forms.Form):
    start_date = MonthYearInFutureField(
        label="When did or will the barrier start to affect trade?",
        help_text="If you don’t know the month, enter 06.",
        error_messages={"required": "Enter a barrier start date"},
        required=False,
    )

    is_dont_know = TrueFalseBooleanField(
        label="I don't know",
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "govuk-checkboxes__input",
                "aria-describedby": "is_dont_know-hint",
            },
        ),
    )

    is_currently_active = YesNoBooleanField(
        label="Is the barrier currently affecting trade?",
        required=False,
        error_messages={"required": "Enter yes or no"},
        widget=forms.RadioSelect(
            attrs={
                "class": "govuk-radios__input",
                "aria-describedby": "is_currently_active-hint",
            },
        ),
        choices=(("yes", "Yes"), ("no", "No, not yet")),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["start_date"].initial = self.barrier.start_date
        self.fields["is_dont_know"].initial = (
            "True" if not self.barrier.start_date else "False"
        )
        self.fields["is_currently_active"].initial = (
            "yes" if self.barrier.is_currently_active else "no"
        )

    @property
    def barrier(self):
        client = MarketAccessAPIClient(self.token)
        return client.barriers.get(id=self.barrier_id)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        is_dont_know = cleaned_data.get("is_dont_know")

        if not start_date and not is_dont_know:
            raise forms.ValidationError(
                "Enter a barrier start date or select I don't know"
            )

        return cleaned_data

    def clean_start_date(self):
        if start_data := self.cleaned_data["start_date"]:
            return start_data.isoformat()
        return None

    def save(self):
        client = MarketAccessAPIClient(self.token)

        start_date = self.cleaned_data.get("start_date")
        is_currently_active = self.cleaned_data.get("is_currently_active")

        client.barriers.patch(
            id=str(self.barrier_id),
            start_date=start_date,
            is_currently_active=is_currently_active,
        )
