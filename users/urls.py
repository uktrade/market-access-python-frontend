from django.urls import path

from .views import (
    Login,
    LoginCallback,
    SignOut,
    AddUserToGroup,
    UserPermissions,
    PermissionsUserSearch,
)

app_name = "users"

urlpatterns = [
    path('login/', Login.as_view(), name="login"),
    path('login/callback/', LoginCallback.as_view(), name="login_callback"),
    path('sign-out/', SignOut.as_view(), name="sign-out"),
    path('permissions/', UserPermissions.as_view(), name="user_permissions"),
    path('permissions/add-user/', PermissionsUserSearch.as_view(), name="permissions_user_search"),
    path('permissions/users/<uuid:user_id>/add/', AddUserToGroup.as_view(), name="add_user_to_group"),
]
