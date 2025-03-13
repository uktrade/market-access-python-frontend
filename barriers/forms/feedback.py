from django import forms

from utils.api.client import MarketAccessAPIClient


class FeedbackForm(forms.Form):
    satisfaction = forms.ChoiceField(
        label="Overall, how would you rate your experience with Digital Market Access Service (DMAS) today?",
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
        label="What did you do on the Digital Market Access Service today?",
        help_text="Select all that apply.",
        choices=(
            ("REPORT_BARRIER", "Report a barrier"),
            ("SEARCH", "Search for a barrier"),
            ("PROGRESS_UPDATE", "Add a progress update to a barrier"),
            ("PROGRAM_FUND_UPDATE", "Add a programme fund to a barrier"),
            ("EXPORT_BARRIER_CSV", "Download a CSV file"),
            ("PUBLISHING", "Task relating to publishing a barrier to GOV.UK"),
            ("EDIT_BARRIER", "Amend an existing barrier"),
            ("OTHER", "Other"),
            ("DONT_KNOW", "Don't know"),
        ),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "govuk-checkboxes__input"}),
        error_messages={
            "required": "Select one or more activities",
        },
    )
    experienced_issues = forms.MultipleChoiceField(
        label="Did you experience any issues?",
        help_text="Select all that apply.",
        choices=(
            ("NO_ISSUE", "I did not experience any issues"),
            ("UNABLE_TO_FIND", "I did not find what I was looking for"),
            ("DIFFICULT_TO_NAVIGATE", "I found it difficult to navigate"),
            ("LACKS_FEATURE", "The service lacks a feature I need"),
            ("UNABLE_TO_LOAD", "I was unable to load, refresh or enter a page"),
            ("OTHER", "Other"),
        ),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "govuk-checkboxes__input"}),
        error_messages={
            "required": 'Select the type of issue you experienced, or select "I did not experience any issues"',
        },
        required=False,
    )
    other_detail = forms.CharField(
        label="Describe the issue you faced",
        # help_text="",
        max_length=1200,
        required=False,
        widget=forms.Textarea(attrs={"class": "govuk-textarea", "rows": 7}),
    )
    feedback_text = forms.CharField(
        label="How could we improve the service?",
        help_text="Do not include any personal information, like your name or email address.",
        max_length=1200,
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
        issues = cleaned_data.get("experienced_issues", None)
        if not satisfaction or not issues and csat_submission != "True":
            if not satisfaction:
                self.add_error("satisfaction", "Select a level of satisfaction")
            if not issues:
                self.add_error(
                    "experienced_issues",
                    'Select the type of issue you experienced, or select "I did not experience any issues"',
                )
        elif csat_submission == "True":
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
