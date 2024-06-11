import dateutil.parser

from utils.models import APIModel


class Mention(APIModel):
    def __init__(self, data):
        self.data = data

    @property
    def created_on(self):
        return dateutil.parser.parse(self.data["created_on"])

    @property
    def go_to_url_path(self):
        data2 = self.data
        return self.data["go_to_url_path"]

    @property
    def read_by_recipient(self):
        return self.data["read_by_recipient"]


class NotificationExclusion(APIModel):
    def __init__(self, data):
        self.data = data

    @property
    def mention_notifications_enabled(self):
        return self.data["mention_notifications_enabled"]
