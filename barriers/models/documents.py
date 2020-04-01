from utils.models import APIModel


class Document(APIModel):
    """
    Wrapper around API document data
    """

    def __init__(self, data):
        self.data = data
        self.id = data["id"]
        self.name = data["name"]
        self.size = data["size"]
        self.can_download = data["status"] == "virus_scanned"
        self.status = data["status"]

    @property
    def readable_status(self):
        return {
            "not_virus_scanned": "Not virus scanned",
            "virus_scanning_scheduled": "Virus scanning scheduled",
            "virus_scanning_in_progress": "Virus scanning in progress",
            "virus_scanning_failed": "Virus scanning failed.",
            "virus_scanned": "Virus scanned",
            "deletion_pending": "Deletion pending",
        }.get(self.status)
