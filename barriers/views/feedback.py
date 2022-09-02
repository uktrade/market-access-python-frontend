from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from barriers.forms.feedback import FeedbackForm


class FeedbackFormView(FormView):
    template_name = "feedback.html"
    form_class = FeedbackForm
    success_url = reverse_lazy("core:feedback-thanks")

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["token"] = self.request.session.get("sso_token")
        return form_kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class FeedbackGratitudeView(TemplateView):
    template_name = "feedback-thanks.html"
