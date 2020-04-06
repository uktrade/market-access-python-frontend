from django import forms

from utils.metadata import get_metadata


class BarrierSource:
    """
    Source as in:
     - Where did you hear about the barrier?
     - Who told you about it?
    """
    COMPANY = "COMPANY"
    TRADE = "TRADE"
    GOVT = "GOVT"
    OTHER = "OTHER"

    @classmethod
    def choices(cls):
        return (
            (cls.COMPANY, "Company"),
            (cls.TRADE, "Trade association"),
            (cls.GOVT, "Government entity"),
            (cls.OTHER, "Other"),
        )


class RelatedToBrexit:
    YES = 1
    NO = 2
    DONT_KNOW = 3

    @classmethod
    def choices(cls):
        return (
            (cls.YES, "Yes"),
            (cls.NO, "No"),
            (cls.DONT_KNOW, "Don't know"),
        )


class NewReportBarrierAboutForm(forms.Form):
    BS = BarrierSource()
    barrier_title = forms.CharField(
        label="Name this barrier",
        help_text="Include the name of the product, "
                  "service or investment and the type of problem. "
                  "For example, Import quotas for steel rods.",
        error_messages={'required': "Enter a name for this barrier"},
    )
    product = forms.CharField(
        label="What product, service or investment is affected?",
        error_messages={'required': "Enter a product, service or investment"},
    )
    source = forms.ChoiceField(
        label="Who told you about the barrier?",
        choices=BS.choices(),
        error_messages={
            'required': "Select how you became aware of the barrier"
        },
    )
    other_source = forms.CharField(
        label="Please specify",
        required=False,
        max_length=255,
        error_messages={
            'required': "Select how you became aware of the barrier",
            "max_length": "Other source should be %(limit_value)d characters or fewer",
        },
    )
    tags = forms.MultipleChoiceField(
        choices=[],
        widget=forms.CheckboxSelectMultiple,
        label="Is this issue caused by or related to any of the following?"
    )

    def __init__(self, tags, *args, **kwargs):
        super().__init__(*args, **kwargs)
        metadata = get_metadata()
        self.fields["tags"].choices = metadata.get_barrier_tag_report_choices()
