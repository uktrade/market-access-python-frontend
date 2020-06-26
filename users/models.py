from utils.models import APIModel


class Group(APIModel):
    @property
    def plural_name(self):
        return f"{self.name}s"


class User(APIModel):
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
