from django.views.generic import FormView

from barriers.forms.feedback import FeedbackForm


class FeedbackFormView(FormView):
    template_name = "feedback.html"
    form_class = FeedbackForm
