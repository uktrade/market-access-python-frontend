from reports.model_forms.new_report_barrier_about import NewReportBarrierAboutForm
from reports.model_forms.new_report_barrier_summary import NewReportBarrierSummaryForm


class NewReportBarrierAboutAndSummary(
    NewReportBarrierAboutForm, NewReportBarrierSummaryForm
):
    pass
