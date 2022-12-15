from __future__ import annotations

from typing import TYPE_CHECKING

from reports.model_forms.new_report_barrier_about import NewReportBarrierAboutForm
from reports.model_forms.new_report_barrier_summary import NewReportBarrierSummaryForm

if TYPE_CHECKING:
    from reports.models import Report


class NewReportBarrierAboutAndSummary(
    NewReportBarrierAboutForm, NewReportBarrierSummaryForm
):
    field_order = [
        "title",
        "summary",
        "is_summary_sensitive",
        "product",
        "source",
        "other_source",
    ]

    @staticmethod
    def get_barrier_initial(barrier: Report):
        return {
            **NewReportBarrierAboutForm.get_barrier_initial(barrier),
            **NewReportBarrierSummaryForm.get_barrier_initial(barrier),
        }
