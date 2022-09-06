from urllib.parse import quote

from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from barriers.forms.feedback import FeedbackForm


class FeedbackFormView(FormView):
    template_name = "feedback.html"
    form_class = FeedbackForm
    success_url = reverse_lazy("core:feedback-thanks")

    def get_context_data(self, **kwargs):
        kwargs["return_url"] = self.request.GET.get("return", "/")
        return super().get_context_data(**kwargs)

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["token"] = self.request.session.get("sso_token")
        return form_kwargs

    def get_success_url(self):
        return_url = quote(self.request.GET.get("return", "/"))
        return f"{self.success_url}?return={return_url}"

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class FeedbackGratitudeView(TemplateView):
    template_name = "feedback-thanks.html"

    def get_context_data(self, **kwargs):
        kwargs["return_url"] = self.request.GET.get("return", "/")
        return super().get_context_data(**kwargs)
