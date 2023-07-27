from django.urls import path
from django.views.generic import TemplateView

from barriers.views.feedback import FeedbackFormView, FeedbackGratitudeView
from utils.company_search import SearchCompany

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
    path(
        "feedback/thankyou/",
        FeedbackGratitudeView.as_view(),
        name="feedback-thanks",
    ),
    path(
        "companies/search/<str:search_term>/",
        SearchCompany.as_view(),
        name="search_company",
    ),
]
