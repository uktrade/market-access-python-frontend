from utils.models import APIModel


class PermissionGroup(APIModel):
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
