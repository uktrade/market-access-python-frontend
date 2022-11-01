import logging

from django import forms

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
from utils.forms import (
    ChoiceFieldWithHelpText,
    ClearableMixin,
    MonthYearInFutureField,
    MultipleChoiceFieldWithHelpText,
    YesNoBooleanField,
    YesNoDontKnowBooleanField,
)

from .mixins import APIFormMixin

logger = logging.getLogger(__name__)


class UpdateCommercialValueForm(APIFormMixin, forms.Form):
    commercial_value = forms.IntegerField(
        min_value=0,
        max_value=1000000000000,
        localize=True,
        label="What is the value of the barrier to the affected business(es) in GBP?",
        error_messages={
            "required": "Enter a value",
            "min_value": "Enter a valid number",
            "max_value": "Enter a valid number",
        },
    )
    commercial_value_explanation = forms.CharField(
        widget=forms.Textarea,
        error_messages={"required": "Enter a value description and timescale"},
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
        label="Give us a summary of the barrier and how you found out about it",
        widget=forms.Textarea,
        error_messages={"required": "Enter a brief description for this barrier"},
    )
    is_summary_sensitive = YesNoBooleanField(
        label="Does the summary contain OFFICIAL-SENSITIVE information?",
        error_messages={
            "required": (
                "Indicate if summary contains OFFICIAL-SENSITIVE information or not"
            )
        },
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            summary=self.cleaned_data["summary"],
            is_summary_sensitive=self.cleaned_data["is_summary_sensitive"],
        )


class Top100ProgressUpdateForm(APIFormMixin, forms.Form):
    CHOICES = [
        ("ON_TRACK", "On track"),
        ("RISK_OF_DELAY", "Risk of delay"),
        ("DELAYED", "Delayed"),
    ]
    status = forms.ChoiceField(
        label="Delivery confidence",
        choices=CHOICES,
        widget=forms.RadioSelect,
        error_messages={"required": "Select if delivery is on track, at risk of delay or delayed"},
    )
    update = forms.CharField(
        label="Current status",
        help_text=(
            "Include the barrier status, recent progress, and any obstacles. Content"
            " will be used for monthly reports and therefore should be appropriate for"
            " senior stakeholders (including Ministers)."
        ),
        widget=forms.Textarea,
        error_messages={
            "required": "Enter a status update",
        },
    )
    next_steps = forms.CharField(
        label="Next steps",
        help_text=(
            "Outline planned actions over the coming months, including internal to"
            " Government, with industry, and with foreign governments/agencies. Content"
            " will be used for monthly reports and therefore should be appropriate for"
            " senior stakeholders (including Ministers)."
        ),
        widget=forms.Textarea,
        error_messages={"required": "Enter an outline of your next steps"},
    )

    def __init__(self, barrier_id, progress_update_id=None, *args, **kwargs):
        self.barrier_id = barrier_id
        self.progress_update_id = progress_update_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.progress_update_id:
            client.barriers.patch_top_100_progress_update(
                barrier=self.barrier_id,
                id=self.progress_update_id,
                status=self.cleaned_data["status"],
                message=self.cleaned_data["update"],
                next_steps=self.cleaned_data["next_steps"],
            )
        else:
            client.barriers.create_top_100_progress_update(
                barrier=self.barrier_id,
                status=self.cleaned_data["status"],
                message=self.cleaned_data["update"],
                next_steps=self.cleaned_data["next_steps"],
            )


class ProgrammeFundProgressUpdateForm(APIFormMixin, forms.Form):
    milestones_and_deliverables = forms.CharField(
        label="Milestones and deliverables",
        help_text=(
            "Tell us whether your milestones and deliverables from your project plan"
            " are on track or not, any new risks or issues and how you’re managing"
            " them, and if you need any support."
        ),
        widget=forms.Textarea,
        error_messages={
            "required": "Enter your milestones and deliverables",
        },
    )
    expenditure = forms.CharField(
        label="Expenditure",
        help_text=(
            "Tell us how much money you’ve spent so far, what it was spent on and when,"
            " whether your spending is on track with your project plan projection and"
            " whether there’s a risk of over or underspend for this financial year."
        ),
        widget=forms.Textarea,
        error_messages={"required": "Enter your expenditure"},
    )

    def __init__(self, barrier_id, programme_fund_update_id=None, *args, **kwargs):
        self.barrier_id = barrier_id
        self.programme_fund_update_id = programme_fund_update_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.programme_fund_update_id:
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


class UpdateBarrierSourceForm(APIFormMixin, forms.Form):
    CHOICES = [
        ("COMPANY", "Company"),
        ("TRADE", "Trade association"),
        ("GOVT", "Government entity"),
        ("OTHER", "Other "),
    ]
    source = forms.ChoiceField(
        label="How did you find out about the barrier?",
        choices=CHOICES,
        widget=forms.RadioSelect,
        error_messages={"required": "Select how you became aware of the barrier"},
    )
    other_source = forms.CharField(
        label="Please specify",
        required=False,
        max_length=255,
        error_messages={
            "max_length": "Entry should be %(limit_value)d characters or less",
        },
    )

    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get("source")
        other_source = cleaned_data.get("other_source")

        if source == "OTHER":
            if not other_source and "other_source" not in self.errors:
                self.add_error(
                    "other_source", "Enter how you became aware of the barrier"
                )
        else:
            cleaned_data["other_source"] = ""

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            source=self.cleaned_data["source"],
            other_source=self.cleaned_data["other_source"],
        )


class EditBarrierPriorityForm(APIFormMixin, forms.Form):
    regional_help_text = (
        "It could be relevant to several countries or part of a regional trade plan,"
        " for example, but should be agreed with your regional market access coordinator."
    )
    country_help_text = "Actively being worked on by you or your team."
    watchlist_help_text = "Of potential interest but not actively being worked on."
    CHOICES = [
        (
            "REGIONAL",
            "<span class='govuk-body'>Regional priority</span> <span"
            f" class='govuk-hint'>{regional_help_text}</span>",
        ),
        (
            "COUNTRY",
            "<span class='govuk-body'>Country priority</span> <span"
            f" class='govuk-hint'>{country_help_text}</span>",
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

    def clean(self):
        cleaned_data = super().clean()
        priority_level = cleaned_data.get("priority_level")
        top_priority = cleaned_data.get("top_barrier")

        # Need to check that the barrier is not already a Top 100 or awaiting approval
        client = MarketAccessAPIClient(self.token)
        existing_top_priority_status = getattr(
            client.barriers.get(id=self.id), "top_priority_status"
        )

        # If top 100 question not answered, default to "NONE"
        if top_priority is None or top_priority == "":
            top_priority = "NONE"

        # Need to catch attempts to change a top priority barrier to watchlist priority level
        # But only when adding a new status
        if (
            priority_level == "WATCHLIST"
            and top_priority != "NONE"
            and existing_top_priority_status == "NONE"
        ):
            self.add_error(
                "priority_level",
                "Top 100 barriers must have regional or country level priority",
            )

    def save(self):
        client = MarketAccessAPIClient(self.token)

        # Get a list of the tag ids already attached to the barrier
        existing_tags = getattr(client.barriers.get(id=self.id), "tags")
        tag_ids = []
        for tag in existing_tags:
            tag_ids.append(tag["id"])

        patch_args = {
            "id": self.id,
            "priority_level": self.cleaned_data["priority_level"],
            "tags": tag_ids,
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

        # Need to be able to wipe Top 100 APPROVAL_PENDING with a change to the watchlist priority
        if (
            self.cleaned_data["priority_level"] == "WATCHLIST"
            and existing_top_priority_status == "APPROVAL_PENDING"
        ):
            patch_args["top_priority_status"] = "NONE"

        # Need to be able to request removal automatically if changine a Top 100 barrier to watchlist
        if (
            self.cleaned_data["priority_level"] == "WATCHLIST"
            and existing_top_priority_status == "APPROVED"
        ):
            patch_args["top_priority_status"] = "REMOVAL_PENDING"

        # Set additional args depending on if questions are answered
        if self.fields.get("priority_summary"):
            patch_args["priority_summary"] = self.cleaned_data["priority_summary"]

        if self.fields.get("top_priority_rejection_summary"):
            patch_args["top_priority_rejection_summary"] = self.cleaned_data[
                "top_priority_rejection_summary"
            ]

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
            show_reason_for_top_priority_field = False
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
                help_text="This is the government's global list of priority market access barriers.",
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

        def clean_top_barrier(self):
            cleaned_priority_input = self.cleaned_data.get("priority_level")
            cleaned_top_priority_status = self.cleaned_data.get("top_barrier")

            # If user has entered a priority other than Watchlist, we need an answer for
            # top priority status.
            if (
                cleaned_priority_input in ["COUNTRY", "REGIONAL"]
                and cleaned_top_priority_status == ""
            ):
                raise forms.ValidationError(
                    "Please indicate if this is a top priority barrier"
                )
            return cleaned_top_priority_status

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


class UpdateBarrierTermForm(APIFormMixin, forms.Form):
    CHOICES = [
        (
            1,
            "A procedural, short-term barrier",
            "for example, goods stuck at the border or documentation issue",
        ),
        (
            2,
            "A long-term strategic barrier",
            "for example, a change of regulation",
        ),
    ]
    term = ChoiceFieldWithHelpText(
        label="What is the scope of the barrier?",
        choices=CHOICES,
        widget=forms.RadioSelect,
        error_messages={"required": "Select a barrier scope"},
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(id=self.id, term=self.cleaned_data["term"])


class UpdateBarrierEstimatedResolutionDateForm(
    ClearableMixin, APIFormMixin, forms.Form
):
    estimated_resolution_date = MonthYearInFutureField(
        label="Estimated resolution date",
        help_text="For example, 11 2024",
        error_messages={"required": "Enter an estimated resolution date"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        estimated_resolution_date = kwargs.get("initial", {}).get(
            "estimated_resolution_date"
        )
        if estimated_resolution_date:
            self.fields[
                "estimated_resolution_date"
            ].label = "Change estimated resolution date"

    def clean_estimated_resolution_date(self):
        return self.cleaned_data["estimated_resolution_date"].isoformat()

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            estimated_resolution_date=self.cleaned_data.get(
                "estimated_resolution_date"
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
        error_messages={
            "required": (
                "Select yes if the barrier is eligible for an initial economic"
                " assessment"
            )
        },
    )
    economic_assessment_eligibility_summary = forms.CharField(
        label="Why is this barrier not eligible for an initial economic assessment?",
        help_text="Please explain why this barrier is not eligible",
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
                    "Enter why this barrier is not eligible",
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
