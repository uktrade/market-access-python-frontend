from django.urls import path
from django.utils.decorators import decorator_from_middleware

from .middleware import StatsMiddleware
from .views import HealthCheckView

app_name = "healthcheck"

urlpatterns = [
    path(
        "check/",
        decorator_from_middleware(StatsMiddleware)(HealthCheckView.as_view()),
        name="check"
    ),
]
