import dateutil.parser

from django.urls import reverse

from utils.models import APIModel


class BarrierDownload(APIModel):
    data_fields = ("created_on", "modified_on")

    def __init__(self, data):
        self.data = data

    @property
    def id(self):
        return self.data.get("id")

    @property
    def name(self):
        name = self.data.get("name")
        return name or self.data.get("filename")
    
    @property
    def created_on(self):
        return dateutil.parser.parse(self.data["created_on"])
    
    @property
    def modified_on(self):
        return dateutil.parser.parse(self.data["modified_on"])

    @property
    def status(self):
        STATUS = {
            "PENDING": "Pending",
            "PROCESSING": "Processing",
            "COMPLETE": "Complete",
            "FAILED": "Failed",
        }
        return STATUS.get(self.data.get("status"), "Unknown")

    @property
    def created_by(self):
        return self.data.get("created_by")
    
    @property
    def filters(self):
        return self.data.get("filters")
    
    @property
    def count(self):
        return self.data.get("count")
    
    @property
    def success(self):
        return self.data.get("success")
    
    @property
    def reason(self):
        return self.data.get("reason")

    @property
    def progress_url(self):
        """this property is used in the template to link to the progress page"""

        url = reverse("barriers:download-detail", kwargs={"pk": self.id})
        return url
