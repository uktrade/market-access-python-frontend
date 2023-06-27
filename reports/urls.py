from django.urls import path

# from barriers.views.report_barrier import ReportBarrierAnswersView
# from reports.location_views import NewReportBarrierLocationMasterView
from reports.report_barrier_view import ReportBarrierWizardView

# from reports.report_views import (
#    NewReportBarrierAboutView,
#    NewReportBarrierCategoriesAddView,
#    NewReportBarrierCategoriesDeleteView,
#    NewReportBarrierCategoriesView,
#    NewReportBarrierCommoditiesView,
#    NewReportBarrierHasSectorsView,
#    NewReportBarrierLocationView,
#    NewReportBarrierSectorsAddAllView,
#    NewReportBarrierSectorsAddView,
#    NewReportBarrierSectorsRemoveView,
#    NewReportBarrierSectorsView,
#    NewReportBarrierStatusView,
#    NewReportBarrierSummaryView,
#    NewReportBarrierTradeDirectionView,
#    ReportDetail,
# )
from reports.views import (  # NewReportBarrierAdminAreasView,; NewReportBarrierCausedByTradingBlocView,; NewReportBarrierLocationAddAdminAreasView,; NewReportBarrierLocationHasAdminAreasView,; NewReportBarrierLocationRemoveAdminAreasView,; NewReportStartRedirect,
    DeleteReport,
    DraftBarriers,
    NewReport,
)

app_name = "reports"

urlpatterns = [
    # Two routes into form - one provides a barrier_id (if the draft already exists), one where
    # we make a new 'report' object in the DB
    path("reports/new", NewReport.as_view(), name="new_report"),
    path(
        "reports/start",
        ReportBarrierWizardView.as_view(url_name="reports:report-barrier-wizard-step"),
        name="report-barrier-wizard",
    ),
    path(
        "reports/<str:step>",
        ReportBarrierWizardView.as_view(url_name="reports:report-barrier-wizard-step"),
        name="report-barrier-wizard-step",
    ),
    path(
        "reports/drafts/<uuid:draft_barrier_id>",
        ReportBarrierWizardView.as_view(url_name="reports:report-barrier-wizard-step"),
        name="report-barrier-drafts",
    ),
    path("draft-barriers", DraftBarriers.as_view(), name="draft_barriers"),
    path(
        "reports/<uuid:barrier_id>/delete",
        DeleteReport.as_view(),
        name="delete_report",
    ),
]
