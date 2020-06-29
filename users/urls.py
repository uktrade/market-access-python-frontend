from django.urls import path

from .views import (
    AddUser,
    EditUser,
    Login,
    LoginCallback,
    ManageUsers,
    SignOut,
    UserDetail,
)

app_name = "users"

urlpatterns = [
    path('login/', Login.as_view(), name="login"),
    path('login/callback/', LoginCallback.as_view(), name="login_callback"),
    path('sign-out/', SignOut.as_view(), name="sign-out"),
    path('users/', ManageUsers.as_view(), name="manage_users"),
    path('users/add/', AddUser.as_view(), name="add_user"),
    path('users/<int:user_id>/', UserDetail.as_view(), name="user_detail"),
    path('users/<int:user_id>/edit/', EditUser.as_view(), name="edit_user"),
]
