from .documents import Document

from utils.models import APIModel

import dateutil.parser


class Assessment(APIModel):
    """
    Wrapper around API assessment data
    """

    def __init__(self, data):
        self.data = data
        self.documents = [Document(document) for document in data["documents"]]


class ResolvabilityAssessment(APIModel):
    @property
    def created_on(self):
        return dateutil.parser.parse(self.data["created_on"])

    @property
    def reviewed_on(self):
        if self.data.get("reviewed_on"):
            return dateutil.parser.parse(self.data["reviewed_on"])


class StrategicAssessment(APIModel):
    @property
    def created_on(self):
        return dateutil.parser.parse(self.data["created_on"])

    @property
    def reviewed_on(self):
        if self.data.get("reviewed_on"):
            return dateutil.parser.parse(self.data["reviewed_on"])
