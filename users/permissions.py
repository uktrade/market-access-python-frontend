from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied

from utils.api.client import MarketAccessAPIClient


class APIPermissionMixin(PermissionRequiredMixin):

    def has_permission(self):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        user = client.users.get_current()
        return all(
            user.has_permission(permission)
            for permission in self.get_permission_required()
        )

    def handle_no_permission(self):
        raise PermissionDenied(self.get_permission_denied_message())
