import dateutil.parser
from django.urls import reverse

from barriers.forms.search import BarrierSearchForm
from utils.metadata import get_metadata
from utils.models import APIModel


class BarrierDownload(APIModel):
    data_fields = ("created_on", "modified_on")

    def __init__(self, data):
        self.data = data
        print(self.data)

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
    def status(self) -> str:
        STATUS = {
            "PENDING": "Pending",
            "PROCESSING": "Processing",
            "COMPLETE": "Complete",
            "FAILED": "Failed",
        }
        return STATUS.get(self.data.get("status"), "Unknown")

    @property
    def created_by(self) -> str:
        return self.data.get("created_by")

    @property
    def filters(self) -> dict:
        return self.data.get("filters")

    @property
    def count(self) -> int:
        return self.data.get("count")

    @property
    def success(self) -> bool:
        return self.data.get("success")

    @property
    def reason(self) -> str:
        return self.data.get("reason")

    @property
    def progress_uri(self):
        """this property is used in the template to link to the progress page"""
        return reverse("barriers:download-detail", kwargs={"pk": self.id})

    @property
    def dashboard_uri(self):
        """this property is used in the template to link to the download tab on the dashboard"""
        return reverse("barriers:dashboard") + "?active=barrier_downloads"

    @property
    def readable_filters(self):
        if self._readable_filters is None:
            search_form = BarrierSearchForm(
                metadata=get_metadata(),
                data=self.filters,
            )
            search_form.full_clean()
            self._readable_filters = search_form.get_readable_filters(
                with_remove_urls=False
            )
        return self._readable_filters
