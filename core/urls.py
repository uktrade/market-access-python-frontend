from django.urls import path
from django.views.generic import TemplateView

app_name = "core"

urlpatterns = [
    path('accessibility/', TemplateView.as_view(template_name='accessibility.html'), name="accessibility"),
]
