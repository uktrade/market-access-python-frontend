import dateutil.parser

from utils.models import APIModel

from .documents import Document


class Note(APIModel):
    """
    Wrapper around API interaction data
    """

    model = "note"
    field = "text"
    modifier = "note"

    def __init__(self, data):
        self.data = data
        self.date = dateutil.parser.parse(data["created_on"])
        self.text = data["text"]
        self.user = data["created_by"]
        self.documents = [Document(document) for document in data["documents"]]

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
        }


class PublicBarrierNote(APIModel):
    model = "public_barrier_note"
    field = "text"
    modifier = "note"

    def __init__(self, data):
        self.data = data
        self.date = dateutil.parser.parse(data["created_on"])
        self.text = data["text"]
        self.user = data["created_by"]
