from django.urls import path

from .views import (
    Login,
    LoginCallback,
    SignOut,
)

app_name = "users"

urlpatterns = [
    path("login/", Login.as_view(), name="login"),
    path("login/callback/", LoginCallback.as_view(), name="login_callback"),
    path("sign-out/", SignOut.as_view(), name="sign-out"),
]
