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
