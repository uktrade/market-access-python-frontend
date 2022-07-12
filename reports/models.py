import operator
from enum import Enum

import dateutil.parser
from django.urls import reverse

from barriers.constants import STATUSES, Statuses
from utils.metadata import get_metadata
from utils.models import APIModel


def get_report_stages():
    from reports.forms.new_report_barrier_commodities import (
        NewReportUpdateBarrierCommoditiesForm,
    )
    from reports.model_forms.new_report_barrier_about_and_summary import (
        NewReportBarrierAboutAndSummary,
    )
    from reports.model_forms.new_report_barrier_categories import (
        NewReportBarrierCategoriesForm,
    )
    from reports.model_forms.new_report_barrier_location import (
        NewReportBarrierLocationForm,
    )
    from reports.model_forms.new_report_barrier_sectors import (
        NewReportBarrierSectorsForm,
    )
    from reports.model_forms.new_report_barrier_status import NewReportBarrierStatusForm

    return {
        "About the barrier": {
            "form": NewReportBarrierAboutAndSummary,
            "url_path": "reports:barrier_about_uuid",
        },
        "Barrier status": {
            "form": NewReportBarrierStatusForm,
            "url_path": "reports:barrier_status_uuid",
        },
        "Location of the barrier": {
            "form": NewReportBarrierLocationForm,
            "url_path": "reports:barrier_location_uuid",
        },
        "Sectors affected by the barrier": {
            "form": NewReportBarrierSectorsForm,
            "url_path": "reports:barrier_sectors_uuid",
        },
        "Define barrier category": {
            "form": NewReportBarrierCategoriesForm,
            "url_path": "reports:barrier_categories_uuid",
        },
        "Add HS commodity codes": {
            "form": NewReportUpdateBarrierCommoditiesForm,
            "url_path": "reports:barrier_commodities_uuid",
        },
    }


class ReportStageStatus(Enum):
    NOT_STARTED = 1
    IN_PROGRESS = 2
    COMPLETE = 3


class ReportCompletionMixin(object):
    _stages = None
    _stage_completion = None
    _stage_form_errors = None

    @property
    def REPORT_STAGES(self):
        return get_report_stages()

    @property
    def is_complete(self):
        # are all stages complete
        return all(map(self.is_stage_complete, self.REPORT_STAGES.keys()))

    @property
    def next_stage(self):
        stages = self.stages
        for stage in self.stages:
            if stage["status_code"] != ReportStageStatus.COMPLETE.name:
                return stage
        return None

    def is_stage_complete(self, stage: str):
        if not self._stage_completion:
            self._stage_completion = {}
        if stage in self._stage_completion.keys():
            return self._stage_completion[stage]

        FormClass = self.REPORT_STAGES[stage]["form"]
        form_data = FormClass.get_barrier_initial(self)
        form = FormClass(data=form_data)
        is_valid = form.is_valid()
        self._stage_completion[stage] = is_valid
        return is_valid

    def get_stage_url(self, stage: str):
        return reverse(
            self.REPORT_STAGES[stage]["url_path"], kwargs={"barrier_id": self.id}
        )

    @property
    def stages(self):
        if not self._stages:
            self._stages = []
            for index, (stage_name, stage_param) in enumerate(
                self.REPORT_STAGES.items()
            ):
                is_complete = self.is_stage_complete(stage_name)
                self._stages.append(
                    {
                        "name": stage_name,
                        "stage_code": f"1.{index + 1}",
                        "status_id": ReportStageStatus.COMPLETE.value
                        if is_complete
                        else ReportStageStatus.NOT_STARTED.value,
                        "status_code": ReportStageStatus.COMPLETE.name
                        if is_complete
                        else ReportStageStatus.NOT_STARTED.name,
                        "status_text": "Complete" if is_complete else "In progress",
                        "url": self.get_stage_url(stage_name),
                    }
                )
        return self._stages


class Report(ReportCompletionMixin, APIModel):
    _metadata = None
    _progress = None

    @property
    def id(self):
        return self.data.get("id")

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = get_metadata()
        return self._metadata

    @property
    def resolved_text(self):
        if str(self.status["id"]) == STATUSES.RESOLVED_IN_FULL:
            return "In full"
        elif str(self.status["id"]) == STATUSES.RESOLVED_IN_PART:
            return "In part"
        return "No"

    @property
    def created_on(self):
        return dateutil.parser.parse(self.data["created_on"])

    @property
    def progress(self):
        if self._progress is None:
            self._progress = self.data.get("progress", [])
            self._progress.sort(key=operator.itemgetter("stage_code"))
        return self._progress

    def is_status(self, status_id: Statuses):
        if not self.status:
            return False
        return str(self.status["id"]) == status_id

    @property
    def source_display(self):
        return self.data.get("source", {}).get("name", "")

    @property
    def status_display(self):
        return self.data.get("status", {}).get("name", "")

    @property
    def sub_status_display(self):
        sub_status = self.data.get("sub_status", {}).get("name", "")
        if sub_status == "None":
            return None
        return sub_status

    @property
    def trade_direction_display(self):
        if self.data.get("trade_direction", {}):
            return self.data.get("trade_direction", {}).get("name", "")
        return ""

    @property
    def country_trading_bloc(self):
        # is the barrier tied to a country
        # and does that country have a trading bloc
        country = self.data.get("country", None)
        if not country:
            return False
        return country.get("trading_bloc", False)
