from django.urls import path

from users.account.views import (
    UserEditBarrierLocations,
    UserEditGovernmentDepartment,
    UserEditOverseasRegions,
    UserEditPolicyTeams,
    UserEditSectors,
)
from users.views import (
    Account,
    AccountDownloads,
    AccountDrafts,
    AccountSavedSearch,
    AddUser,
    DeleteUser,
    EditUser,
    ExportUsers,
    GetUsers,
    Login,
    LoginCallback,
    ManageUsers,
    Mentions,
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
        "account/saved_searches/",
        AccountSavedSearch.as_view(),
        name="account_saved_searches",
    ),
    path(
        "account/downloads/",
        AccountDownloads.as_view(),
        name="account_downloads",
    ),
    path(
        "account/drafts/",
        AccountDrafts.as_view(),
        name="account_drafts",
    ),
    path(
        "account/policy-teams/edit/",
        UserEditPolicyTeams.as_view(),
        name="edit_user_policy_teams",
    ),
    path(
        "account/sectors/edit/",
        UserEditSectors.as_view(),
        name="edit_user_sectors",
    ),
    path(
        "account/barrier-locations/edit/",
        UserEditBarrierLocations.as_view(),
        name="edit_user_barrier_locations",
    ),
    path(
        "account/overseas-regions/edit/",
        UserEditOverseasRegions.as_view(),
        name="edit_user_overseas_regions",
    ),
    path(
        "account/government-department/edit/",
        UserEditGovernmentDepartment.as_view(),
        name="edit_user_government_department",
    ),
    path("mentions/", Mentions.as_view(), name="mentions"),
]
