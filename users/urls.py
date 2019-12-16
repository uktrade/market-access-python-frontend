from django.urls import path

from .views import (
    Login,
    LoginCallback,
)

app_name = "users"

urlpatterns = [
    path('login/', Login.as_view(), name="login"),
    path('login/callback/', LoginCallback.as_view(), name="login_callback"),
]
