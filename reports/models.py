from django.db import models

from utils.metadata import get_metadata
from utils.models import APIModel

import dateutil.parser


class Report(APIModel):
    _metadata = None

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = get_metadata()
        return self._metadata

    @property
    def resolved_text(self):
        if self.is_resolved:
            if self.resolved_status == "RESOLVED":
                return "In full"
            return "In part"
        return "No"

    @property
    def country(self):
        return self.metadata.get_country(self.export_country)

    @property
    def problem_status_text(self):
        return self.metadata.get_problem_status(self.problem_status)

    @property
    def created_on(self):
        return dateutil.parser.parse(self.data['created_on'])
