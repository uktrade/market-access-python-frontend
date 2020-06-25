from utils.models import APIModel


class Group(APIModel):
    @property
    def plural_name(self):
        return f"{self.name}s"


class User(APIModel):
    client = None
    is_stale = False

    @property
    def groups_display(self):
        group_names = [group["name"] for group in self.data.get("groups")]
        if group_names:
            return ", ".join(group_names)
        return "General user"

    @property
    def permitted_applications(self):
        return self.data.get("permitted_applications", [])

    def set_client(self, client):
        self.client = client

    def refresh(self):
        if self.client is not None:
            self.data = self.client.users.get_current().data

    @property
    def permissions(self):
        return self.data.get("permissions", [])

    def has_permission(self, permission_name):
        if self.is_stale:
            self.refresh()
            self.is_stale = False

        if self.is_active and self.is_superuser:
            return True
        return permission_name in self.permissions
