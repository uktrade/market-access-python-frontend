from django.urls import path
from django.utils.decorators import decorator_from_middleware

from .middleware import StatsMiddleware
from .views import HealthCheckView, APIHealthCheckView

app_name = "healthcheck"

urlpatterns = [
    path(
        "check-fe/",
        decorator_from_middleware(StatsMiddleware)(HealthCheckView.as_view()),
        name="check-fe"
    ),
    path(
        "check-api/",
        decorator_from_middleware(StatsMiddleware)(APIHealthCheckView.as_view()),
        name="check-api"
    ),
]
