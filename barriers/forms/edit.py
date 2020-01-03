from django import forms

from .mixins import APIFormMixin

from utils.api_client import MarketAccessAPIClient
from utils.forms import ChoiceFieldWithHelpText


class UpdateBarrierTitleForm(APIFormMixin, forms.Form):
    title = forms.CharField(
        label="Suggest a title for this barrier",
        help_text=(
            "Include both the title or service name and the country being "
            "exported to, for example, Import quotas for steel rods in India."
        ),
        max_length=255
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            barrier_title=self.cleaned_data['title']
        )


class UpdateBarrierProductForm(APIFormMixin, forms.Form):
    product = forms.CharField(
        label='What product or service is being exported?',
        max_length=255
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            product=self.cleaned_data['product']
        )


class UpdateBarrierDescriptionForm(APIFormMixin, forms.Form):
    description = forms.CharField(
        label=(
            'Provide a summary of the problem and how you became aware of it'
        ),
        widget=forms.Textarea,
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            problem_description=self.cleaned_data['description']
        )


class UpdateBarrierSourceForm(APIFormMixin, forms.Form):
    CHOICES = [
        ('COMPANY', 'Company'),
        ('TRADE', 'Trade association'),
        ('GOVT', 'Government entity'),
        ('OTHER', 'Other '),
    ]
    source = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    other_source = forms.CharField(label="Please specify", required=False)

    def clean(self):
        cleaned_data = super().clean()
        source = cleaned_data.get("source")
        other_source = cleaned_data.get("other_source")

        if source == "OTHER":
            if not other_source:
                self.add_error(
                    "other_source",
                    "Enter how you became aware of the barrier"
                )
        else:
            cleaned_data['other_source'] = None

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            source=self.cleaned_data['source'],
            other_source=self.cleaned_data['other_source'],
        )


class UpdateBarrierPriorityForm(APIFormMixin, forms.Form):
    CHOICES = [
        ('UNKNOWN', '<strong>Unknown</strong> priority'),
        ('HIGH', '<strong>High</strong> priority'),
        ('MEDIUM', '<strong>Medium</strong> priority'),
        ('LOW', '<strong>Low</strong> priority'),
    ]
    priority = forms.ChoiceField(
        label="What is the priority of the barrier?",
        choices=CHOICES,
        widget=forms.RadioSelect
    )
    priority_summary = forms.CharField(
        label="Why did the priority change? (optional)",
        widget=forms.Textarea,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial_priority = kwargs.get('initial', {}).get('priority')
        if initial_priority == "UNKNOWN":
            self.fields['priority_summary'].label = (
                "Why did you choose this priority? (optional)"
            )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            priority=self.cleaned_data['priority'],
            priority_summary=self.cleaned_data['priority_summary'] or None,
        )


class UpdateBarrierEUExitRelatedForm(APIFormMixin, forms.Form):
    CHOICES = [
        (1, 'Yes'),
        (2, 'No'),
        (3, "Don't know"),
    ]
    eu_exit_related = forms.ChoiceField(
        label='Is this issue caused by or related to EU Exit?',
        choices=CHOICES,
        widget=forms.RadioSelect
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            eu_exit_related=self.cleaned_data['eu_exit_related']
        )


class UpdateBarrierProblemStatusForm(APIFormMixin, forms.Form):
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
    problem_status = ChoiceFieldWithHelpText(
        label='What is the scope of the barrier?',
        choices=CHOICES,
        widget=forms.RadioSelect
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            problem_status=self.cleaned_data['problem_status']
        )


class UpdateBarrierStatusForm(APIFormMixin, forms.Form):
    status = forms.CharField(
        label='Provide a summary of why this barrier is dormant',
        widget=forms.Textarea,
    )

    def save(self):
        client = MarketAccessAPIClient(self.token)
        client.barriers.patch(
            id=self.id,
            status=self.cleaned_data['status']
        )
