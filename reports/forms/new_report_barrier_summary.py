from django import forms


class NewReportBarrierSummaryForm(forms.Form):
    problem_description = forms.CharField(
        label="Describe the barrier",
        help_text="Include how the barrier is affecting the export or investment "
                  "and why the barrier exists. For example, because of specific "
                  "laws or measures, which government body imposed them and any "
                  "political context; the HS code; and when the problem started.",
    )
    next_steps_summary = forms.CharField(
        label="What steps will be taken to resolve the barrier?",
        help_text="Include all your agreed team actions.",
    )
