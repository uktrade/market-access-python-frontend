from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied

from utils.api.client import MarketAccessAPIClient


class APIPermissionMixin(PermissionRequiredMixin):

    def has_permission(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        user_data = client.get("whoami")
        perms = self.get_permission_required()
        user_permissions = user_data.get("permissions", [])
        print(user_permissions)
        return all(perm in user_permissions for perm in perms)

    def handle_no_permission(self):
        raise PermissionDenied(self.get_permission_denied_message())
