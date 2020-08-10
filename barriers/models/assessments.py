from .documents import Document

from utils.models import APIModel


class Assessment(APIModel):
    """
    Wrapper around API assessment data
    """

    def __init__(self, data):
        self.data = data
        self.documents = [Document(document) for document in data["documents"]]
