from django.views.generic import FormView

from barriers.forms.feedback import FeedbackForm


class FeedbackFormView(FormView):
    template_name = "feedback.html"
    form_class = FeedbackForm

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["token"] = self.request.session.get("sso_token")
        return form_kwargs
