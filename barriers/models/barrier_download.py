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
        return self.data.get("name")

    @property
    def status(self):
        return self.data.get("status")

    @property
    def created_by(self):
        return self.data.get("created_by")
    
    @property
    def filters(self):
        return self.data.get("filters")
    
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
