from utils.models import APIModel

from .documents import Document


class WTOProfile(APIModel):
    """
    Wrapper around API WTO Profile data
    """

    @property
    def status_text(self):
        if self.wto_has_been_notified:
            return "Yes"
        elif self.wto_should_be_notified:
            return "No - this barrier should be notified to the WTO"
        return "No - this barrier should not be notified to the WTO"

    @property
    def committee_notification_document(self):
        document = self.data.get("committee_notification_document")
        if document:
            return Document(document)

    @property
    def meeting_minutes(self):
        document = self.data.get("meeting_minutes")
        if document:
            return Document(document)
