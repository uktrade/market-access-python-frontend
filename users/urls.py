from django.urls import path

from users.profile.views.policy_teams import UserEditPolicyTeams
from users.views import (
    Account,
    AddUser,
    DeleteUser,
    EditUser,
    ExportUsers,
    GetUsers,
    Login,
    LoginCallback,
    ManageUsers,
    SignOut,
    UserDetail,
)

app_name = "users"

urlpatterns = [
    path("login/", Login.as_view(), name="login"),
    path("login/callback/", LoginCallback.as_view(), name="login_callback"),
    path("sign-out/", SignOut.as_view(), name="sign-out"),
    path("users/", ManageUsers.as_view(), name="manage_users"),
    path("users/search/", GetUsers.as_view(), name="get_users"),
    path("users/export/", ExportUsers.as_view(), name="export_users"),
    path("users/add/", AddUser.as_view(), name="add_user"),
    path("users/<int:user_id>/", UserDetail.as_view(), name="user_detail"),
    path("users/<int:user_id>/edit/", EditUser.as_view(), name="edit_user"),
    path("users/<int:user_id>/delete/", DeleteUser.as_view(), name="delete_user"),
    path("account/", Account.as_view(), name="account"),
    path(
        "account/<int:user_id>/policy-teams/edit/",
        UserEditPolicyTeams.as_view(),
        name="edit_user_policy_teams",
    ),
]
