from utils.models import APIModel

from .datahub import get_visible_apps


class Group(APIModel):
    @property
    def plural_name(self):
        if "Regional Lead" not in self.name and "Related Barriers" not in self.name:
            return f"{self.name}s"
        else:
            return self.name


class DashboardTask(APIModel):
    def to_dict(self):
        return {
            "barrier_code": self.barrier_code,
            "barrier_title": self.barrier_title,
            "message": self.message,
            "tag": self.tag,
        }


class User(APIModel):
    _apps = None

    @property
    def groups_display(self):
        group_names = [group["name"] for group in self.data.get("groups")]
        if group_names:
            return ", ".join(group_names)
        return "General user"

    @property
    def permitted_applications(self):
        return self.data.get("permitted_applications", [])

    @property
    def permissions(self):
        return self.data.get("permissions", [])

    def has_permission(self, permission_name):
        if not self.is_active:
            return False
        return self.is_superuser or permission_name in self.permissions

    def get_apps(self):
        return get_visible_apps(self)

    @property
    def apps(self):
        if self._apps is None:
            self._apps = self.get_apps()
        return self._apps

    @property
    def has_crm_permission(self):
        for app in self.apps:
            if app["permittedKey"] == "datahub-crm":
                return True
        return False

    @property
    def has_approved_digital_trade_email(self):
        return self.data.get("has_approved_digital_trade_email", False)

    @property
    def policy_teams_display(self):
        return self.data.get("policy_teams")
