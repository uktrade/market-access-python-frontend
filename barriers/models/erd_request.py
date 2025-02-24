from utils.models import APIModel
import dateutil.parser


class ErdRequest(APIModel):
    @property
    def estimated_resolution_date(self):
        if self.data.get("estimated_resolution_date"):
            return dateutil.parser.parse(self.data["estimated_resolution_date"])

    @property
    def created_on(self):
        if self.data.get("created_on"):
            return dateutil.parser.parse(self.data["created_on"])