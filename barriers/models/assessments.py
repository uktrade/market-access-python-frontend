from .documents import Document

from utils.metadata import get_metadata
from utils.models import APIModel


class Assessment(APIModel):
    """
    Wrapper around API assessment data
    """

    def __init__(self, data):
        self.data = data
        metadata = get_metadata()
        self.impact_text = metadata.get_impact_text(self.data.get("impact"))
        self.documents = [Document(document) for document in data["documents"]]
