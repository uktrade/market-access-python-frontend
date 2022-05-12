from django import forms

from barriers.constants import TOP_PRIORITY_BARRIER_STATUS_APPROVAL_CHOICES
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
            "max_length": "Product or service should be %(limit_value)d characters or fewer",
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


class UpdateBarrierProgressUpdateForm(APIFormMixin, forms.Form):
    CHOICES = [
        ("ON_TRACK", "On track"),
        ("RISK_OF_DELAY", "Risk of delay"),
        ("DELAYED", "Delayed"),
    ]
    status = forms.ChoiceField(
        label="Delivery confidence",
        choices=CHOICES,
        widget=forms.RadioSelect,
        error_messages={"required": "Delivery confidence is required"},
    )
    update = forms.CharField(
        label="Current status",
        help_text=(
            "Include the barrier status, recent progress, and any obstacles. Content will be used"
            " for monthly reports and therefore should be appropriate for senior stakeholders"
            " (including Ministers)."
        ),
        widget=forms.Textarea,
        error_messages={
            "required": ("Progress update is required"),
        },
    )
    next_steps = forms.CharField(
        label="Next steps",
        help_text=(
            "Outline planned actions over the coming months, including internal to Government,"
            " with industry, and with foreign governments/agencies. Content will be used for "
            "monthly reports and therefore should be appropriate for senior stakeholders "
            "(including Ministers)."
        ),
        widget=forms.Textarea,
        error_messages={"required": ("Next steps is required")},
    )

    def __init__(self, barrier_id, progress_update_id=None, *args, **kwargs):
        self.barrier_id = barrier_id
        self.progress_update_id = progress_update_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient(self.token)
        if self.progress_update_id:
            client.barriers.patch_progress_update(
                barrier=self.barrier_id,
                id=self.progress_update_id,
                status=self.cleaned_data["status"],
                message=self.cleaned_data["update"],
                next_steps=self.cleaned_data["next_steps"],
            )
        else:
            client.barriers.create_progress_update(
                barrier=self.barrier_id,
                status=self.cleaned_data["status"],
                message=self.cleaned_data["update"],
                next_steps=self.cleaned_data["next_steps"],
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
            "max_length": "Other source should be %(limit_value)d characters or fewer",
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


class UpdateBarrierPriorityForm(APIFormMixin, forms.Form):
    CHOICES = [
        ("UNKNOWN", "<strong>Unknown</strong> priority"),
        ("HIGH", "<strong>High</strong> priority"),
        ("MEDIUM", "<strong>Medium</strong> priority"),
        ("LOW", "<strong>Low</strong> priority"),
    ]
    priority = forms.ChoiceField(
        label="What is the priority of the barrier?",
        choices=CHOICES,
        widget=forms.RadioSelect,
        error_messages={"required": "Select a barrier priority"},
    )
    top_barrier = forms.ChoiceField(
        label="Should this barrier be considered a top priority?",
        choices=TOP_PRIORITY_BARRIER_STATUS_APPROVAL_CHOICES,
        widget=forms.RadioSelect,
        error_messages={
            "required": "Please indicate if this is a top priority barrier"
        },
    )
    priority_summary = forms.CharField(
        label="Why did the priority change? (optional)",
        widget=forms.Textarea,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_priority = kwargs.get("initial", {}).get("priority")
        if initial_priority == "UNKNOWN":
            self.fields[
                "priority_summary"
            ].label = "Why did you choose this priority? (optional)"

    def save(self):
        client = MarketAccessAPIClient(self.token)

        # Get a list of the tag ids already attached to the barrier
        existing_tags = getattr(client.barriers.get(id=self.id), "tags")
        tag_ids = []
        for tag in existing_tags:
            tag_ids.append(tag["id"])

        client.barriers.patch(
            id=self.id,
            priority=self.cleaned_data["priority"],
            priority_summary=self.cleaned_data["priority_summary"],
            top_priority_status=self.cleaned_data["top_barrier"],
            tags=tag_ids,
        )


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
        help_text=("For example, 11 2020"),
        error_messages={"required": "Enter the estimated resolution date"},
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


class UpdateBarrierTagsForm(APIFormMixin, forms.Form):
    tags = MultipleChoiceFieldWithHelpText(
        label="Is this issue caused by or related to any of the following?",
        choices=[],
        required=False,
    )
    top_barrier = forms.ChoiceField(
        label="Should this barrier be considered a top priority?",
        choices=TOP_PRIORITY_BARRIER_STATUS_APPROVAL_CHOICES,
        widget=forms.RadioSelect,
        error_messages={
            "required": "Please indicate if this is a top priority barrier"
        },
    )

    def __init__(self, tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tags"].choices = tags

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            tags=self.cleaned_data["tags"],
            top_priority_status=self.cleaned_data["top_barrier"],
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
            "required": ("Indicate if the barrier was caused by the trading bloc")
        },
    )

    def __init__(self, trading_bloc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["caused_by_trading_bloc"].label = (
            f"Was this barrier caused by a regulation introduced by "
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
                "Yes should be selected if the barrier is a local application of an Mercosur "
                "regulation. If it is an Mercosur-wide barrier, the country location should "
                "be changed to Southern Common Market (Mercosur) in the location screen."
            ),
            "TB00013": (
                "Yes should be selected if the barrier is a local application of an EAEU "
                "regulation. If it is an EAEU-wide barrier, the country location should "
                "be changed to Eurasian Economic Union (EAEU) in the location screen."
            ),
            "TB00017": (
                "Yes should be selected if the barrier is a local application of an GCC "
                "regulation. If it is an GCC-wide barrier, the country location should "
                "be changed to Gulf Cooperation Council (GCC) in the location screen."
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
                "Select yes if the barrier is eligible for an initial economic assessment"
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
