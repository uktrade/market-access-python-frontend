from django import forms


class SaveWatchlistForm(forms.Form):
    CHOICES = [
        ('replace', "<strong>Replace</strong> current watch list"),
        ('new', "<strong>Create new</strong> watch list"),
    ]
    name = forms.CharField(label="Name your watch list ")
    replace_or_new = forms.ChoiceField(
        label="How did you find out about the barrier?",
        choices=CHOICES,
        widget=forms.RadioSelect,
    )
