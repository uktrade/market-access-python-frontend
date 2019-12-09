from django import forms

from utils.api_client import MarketAccessAPIClient


class APIFormMixin:
    def __init__(self, id, *args, **kwargs):
        self.id = id
        super().__init__(*args, **kwargs)


class UpdateBarrierTitleForm(APIFormMixin, forms.Form):
    title = forms.CharField(label='Title', max_length=255)

    def save(self):
        client = MarketAccessAPIClient()
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
        client = MarketAccessAPIClient()
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
        client = MarketAccessAPIClient()
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

    def save(self):
        client = MarketAccessAPIClient()
        client.barriers.patch(
            id=self.id,
            source=self.cleaned_data['source']
        )


class UpdateBarrierPriorityForm(APIFormMixin, forms.Form):
    CHOICES = [
        ('UNKNOWN', 'Unknown priority'),
        ('HIGH', 'High priority'),
        ('MEDIUM', 'Medium priority'),
        ('LOW', 'Low priority'),
    ]
    priority = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)
    description = forms.CharField(
        label='Why did you choose this priority? (optional)',
        widget=forms.Textarea,
    )

    def save(self):
        client = MarketAccessAPIClient()
        client.barriers.patch(
            id=self.id,
            priority=self.cleaned_data['priority'],
            priority_description=self.cleaned_data['priority_description']
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
        client = MarketAccessAPIClient()
        client.barriers.patch(
            id=self.id,
            eu_exit_related=self.cleaned_data['eu_exit_related']
        )


class UpdateBarrierProblemStatusForm(APIFormMixin, forms.Form):
    CHOICES = [
        (1, 'A procedural, short-term barrier'),
        (2, 'A long-term strategic barrier'),
    ]
    problem_status = forms.ChoiceField(
        label='What is the scope of the barrier?',
        choices=CHOICES,
        widget=forms.RadioSelect
    )

    def save(self):
        client = MarketAccessAPIClient()
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
        client = MarketAccessAPIClient()
        client.barriers.patch(
            id=self.id,
            status=self.cleaned_data['status']
        )


class AddNoteForm(APIFormMixin, forms.Form):
    text = forms.CharField(
        label=(
            'Add notes on an interaction or event'
        ),
        widget=forms.Textarea,
    )

    def save(self):
        client = MarketAccessAPIClient()
        client.notes.create(
            barrier_id=self.id,
            text=self.cleaned_data['text']
        )


class EditNoteForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)

    def __init__(self, barrier_id, note_id, *args, **kwargs):
        self.barrier_id = barrier_id
        self.note_id = note_id
        super().__init__(*args, **kwargs)

    def save(self):
        client = MarketAccessAPIClient()
        client.notes.update(
            id=self.note_id,
            text=self.cleaned_data['text']
        )
