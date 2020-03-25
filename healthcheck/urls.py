from django.urls import path
from healthcheck.views import HealthCheckView

app_name = "healthcheck"

urlpatterns = [
    path("check/", HealthCheckView.as_view(), name="check"),
]
