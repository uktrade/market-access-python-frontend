from django import forms

from .mixins import APIFormMixin

from utils.api.client import MarketAccessAPIClient
from utils.forms import (
    ChoiceFieldWithHelpText,
    ClearableMixin,
    DayMonthYearField,
    MultipleChoiceFieldWithHelpText,
    YesNoBooleanField,
    YesNoDontKnowBooleanField,
)


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
        }
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
            cleaned_data["other_source"] = None

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
        client.barriers.patch(
            id=self.id,
            priority=self.cleaned_data["priority"],
            priority_summary=self.cleaned_data["priority_summary"] or None,
        )


class UpdateBarrierTermForm(APIFormMixin, forms.Form):
    CHOICES = [
        (
            1,
            "A procedural, short-term barrier",
            "for example, goods stuck at the border or documentation issue",
        ),
        (2, "A long-term strategic barrier", "for example, a change of regulation",),
    ]
    term = ChoiceFieldWithHelpText(
        label="What is the scope of the barrier?",
        choices=CHOICES,
        widget=forms.RadioSelect,
        error_messages={"required": "Select a barrier scope"},
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id, term=self.cleaned_data["term"]
        )


class UpdateBarrierEndDateForm(ClearableMixin, APIFormMixin, forms.Form):
    end_date = DayMonthYearField(
        label="End date",
        help_text=(
            "For example, 30 11 2020. If you don't know the day, please enter 1 for "
            "the first of the month."
        ),
        error_messages={"required": "Enter the end date"},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        end_date = kwargs.get("initial", {}).get("end_date")
        if end_date:
            self.fields["end_date"].label = "Change end date"

    def clean_end_date(self):
        return self.cleaned_data["end_date"].isoformat()

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            end_date=self.cleaned_data.get("end_date"),
        )


class UpdateBarrierTagsForm(APIFormMixin, forms.Form):
    tags = MultipleChoiceFieldWithHelpText(
        label="Is this issue caused by or related to any of the following?",
        choices=[],
        required=False,
    )

    def __init__(self, tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tags"].choices = tags

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(id=self.id, tags=self.cleaned_data["tags"])


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
            "required": (
                "Indicate if the barrier was caused by the trading bloc"
            )
        },
    )

    def __init__(self, trading_bloc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["caused_by_trading_bloc"].label = (
            f"Was this barrier caused by a regulation introduced by "
            f"{trading_bloc['short_name']}?"
        )
        self.fields["caused_by_trading_bloc"].help_text = (
            self.get_help_text(trading_bloc.get("code"))
        )

    def get_help_text(self, trading_bloc_code):
        help_text = {
            "TB00016": (
                "Yes should be selected if the barrier is a local application of an EU "
                "regulation. If it is an EU-wide barrier, the country location should "
                "be changed to EU in the location screen."
            )
        }
        return help_text.get(trading_bloc_code, "")


class UpdateCausedByTradingBlocForm(APIFormMixin, CausedByTradingBlocForm):
    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            caused_by_trading_bloc=self.cleaned_data["caused_by_trading_bloc"],
        )
