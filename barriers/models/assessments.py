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
