from django import forms

from utils.api.client import MarketAccessAPIClient


class FeedbackForm(forms.Form):
    satisfaction = forms.ChoiceField(
        label="1. Overall, how do you feel about your use of the Digital Market Access Service (DMAS) today?",
        choices=(
            ("VERY_SATISFIED", "Very satisfied"),
            ("SATISFIED", "Satisfied"),
            ("NEITHER", "Neither satisfied nor dissatisfied"),
            ("DISSATISFIED", "Dissatisfied"),
            ("VERY_DISSATISFIED", "Very dissatisfied"),
        ),
        widget=forms.RadioSelect(attrs={"class": "govuk-radios__input"}),
        required=False,
    )
    attempted_actions = forms.MultipleChoiceField(
        label="2. What were you trying to do today?",
        help_text="Select all that apply.",
        choices=(
            ("REPORT_BARRIER", "Report a barrier"),
            ("PROGRESS_UPDATE", "Set a progress update"),
            ("EXPORT_BARRIER_CSV", "Export a barrier CSV report"),
            ("ACTION_PLAN", "Create or edit an action plan"),
            ("OTHER", "Other"),
            ("DONT_KNOW", "Don't know"),
        ),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "govuk-checkboxes__input"}),
        error_messages={
            "required": "You must select one or more activities",
        },
    )
    feedback_text = forms.CharField(
        label="3. How could we improve the service?",
        help_text="Don't include any personal information, like your name or email address.",
        max_length=3000,
        required=False,
        widget=forms.Textarea(attrs={"class": "govuk-textarea", "rows": 7}),
    )
    csat_submission = forms.CharField()
    csat_submission_id = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop("token", None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        satisfaction = cleaned_data.get("satisfaction", None)
        csat_submission = cleaned_data.get("csat_submission", False)
        if csat_submission == "False" and (satisfaction is None or satisfaction == ""):
            self.add_error("satisfaction", "You must select a level of satisfaction")
        if csat_submission == "True":
            client = MarketAccessAPIClient(self.token)
            feedback = client.feedback.send_feedback(
                token=self.token, **self.cleaned_data
            )
            self.data = self.data.copy()
            self.data["csat_submission_id"] = feedback["id"]
            # Request extra feedback
            # self.add_error("feedback_text", "Tell us how we can improve")
            raise forms.ValidationError("Let us know how we can improve")
        return cleaned_data

    def save(self):
        client = MarketAccessAPIClient(self.token)
        csat_submission_id = self.cleaned_data.get("csat_submission_id")
        if csat_submission_id == "None":
            client.feedback.send_feedback(token=self.token, **self.cleaned_data)
        else:
            client.feedback.add_comments(
                token=self.token, feedback_id=csat_submission_id, **self.cleaned_data
            )
