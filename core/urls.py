from django.urls import path
from django.views.generic import TemplateView

from barriers.views.feedback import FeedbackFormView

app_name = "core"

urlpatterns = [
    path(
        "accessibility/",
        TemplateView.as_view(template_name="accessibility.html"),
        name="accessibility",
    ),
    path(
        "feedback/",
        FeedbackFormView.as_view(),
        name="feedback",
    ),
]
