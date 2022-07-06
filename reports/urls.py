from django.urls import path

from barriers.views.report_barrier import ReportBarrierAnswersView
from reports.location_views import NewReportBarrierLocationMasterView
from reports.report_views import (
    NewReportBarrierAboutView,
    NewReportBarrierCategoriesAddView,
    NewReportBarrierCategoriesDeleteView,
    NewReportBarrierCategoriesView,
    NewReportBarrierLocationView,
    NewReportBarrierSectorsAddAllView,
    NewReportBarrierSectorsAddView,
    NewReportBarrierSectorsRemoveView,
    NewReportBarrierSectorsView,
    NewReportBarrierStatusView,
    NewReportBarrierSummaryView,
    NewReportBarrierTradeDirectionView,
    ReportDetail,
)
from reports.views import (  # NewReportBarrierTermView,; NewReportBarrierLocationView,
    DeleteReport,
    DraftBarriers,
    NewReport,
    NewReportBarrierAdminAreasView,
    NewReportBarrierCausedByTradingBlocView,
    NewReportBarrierCommoditiesView,
    NewReportBarrierHasSectorsView,
    NewReportBarrierLocationAddAdminAreasView,
    NewReportBarrierLocationHasAdminAreasView,
    NewReportBarrierLocationRemoveAdminAreasView,
    NewReportStartRedirect,
)

app_name = "reports"

urlpatterns = [
    path("draft-barriers/", DraftBarriers.as_view(), name="draft_barriers"),
    path("reports/new/", NewReport.as_view(), name="new_report"),
    path(
        "reports/<uuid:barrier_id>/",
        ReportDetail.as_view(),
        name="draft_barrier_details_uuid",
    ),
    path(
        "reports/<uuid:barrier_id>/delete/",
        DeleteReport.as_view(),
        name="delete_report",
    ),
    # Problem Status
    path("reports/new/start/", NewReportStartRedirect.as_view(), name="barrier_start"),
    path(
        "reports/<uuid:barrier_id>/start/",
        NewReportStartRedirect.as_view(),
        name="barrier_start_uuid",
    ),
    # Problem Status
    # path("reports/new/term/", NewReportBarrierTermView.as_view(), name="barrier_term"),
    # path(
    #     "reports/<uuid:barrier_id>/term/",
    #     NewReportBarrierTermView.as_view(),
    #     name="barrier_term_uuid",
    # ),
    # Status
    path(
        "reports/new/start/is-resolved/",
        NewReportBarrierStatusView.as_view(),
        name="barrier_status",
    ),
    path(
        "reports/<uuid:barrier_id>/is-resolved/",
        NewReportBarrierStatusView.as_view(),
        name="barrier_status_uuid",
    ),
    # Location
    path(
        "reports/new/country/",
        NewReportBarrierLocationMasterView.as_view(),
        name="barrier_location",
    ),
    path(
        "reports/<uuid:barrier_id>/country/",
        NewReportBarrierLocationView.as_view(),
        name="barrier_location_uuid",
    ),
    path(
        "reports/new/country/admin-areas/",
        NewReportBarrierAdminAreasView.as_view(),
        name="barrier_admin_areas",
    ),
    path(
        "reports/<uuid:barrier_id>/country/admin-areas/",
        NewReportBarrierAdminAreasView.as_view(),
        name="barrier_admin_areas_uuid",
    ),
    path(
        "reports/new/country/has-admin-areas/",
        NewReportBarrierLocationHasAdminAreasView.as_view(),
        name="barrier_has_admin_areas",
    ),
    path(
        "reports/<uuid:barrier_id>/country/has-admin-areas/",
        NewReportBarrierLocationHasAdminAreasView.as_view(),
        name="barrier_has_admin_areas_uuid",
    ),
    path(
        "reports/new/country/admin-areas/add/",
        NewReportBarrierLocationAddAdminAreasView.as_view(),
        name="barrier_add_admin_areas",
    ),
    path(
        "reports/<uuid:barrier_id>/country/admin-areas/add/",
        NewReportBarrierLocationAddAdminAreasView.as_view(),
        name="barrier_add_admin_areas_uuid",
    ),
    path(
        "reports/new/country/admin-areas/remove/",
        NewReportBarrierLocationRemoveAdminAreasView.as_view(),
        name="barrier_remove_admin_areas",
    ),
    path(
        "reports/<uuid:barrier_id>/country/admin-areas/remove/",
        NewReportBarrierLocationRemoveAdminAreasView.as_view(),
        name="barrier_remove_admin_areas_uuid",
    ),
    path(
        "reports/new/trade-direction/",
        NewReportBarrierTradeDirectionView.as_view(),
        name="barrier_trade_direction",
    ),
    path(
        "reports/<uuid:barrier_id>/trade-direction/",
        NewReportBarrierTradeDirectionView.as_view(),
        name="barrier_trade_direction_uuid",
    ),
    path(
        "reports/new/caused-by-trading-bloc/",
        NewReportBarrierCausedByTradingBlocView.as_view(),
        name="barrier_caused_by_trading_bloc",
    ),
    path(
        "reports/<uuid:barrier_id>/caused-by-trading-bloc/",
        NewReportBarrierCausedByTradingBlocView.as_view(),
        name="barrier_caused_by_trading_bloc_uuid",
    ),
    # Sectors
    path(
        "reports/<uuid:barrier_id>/has-sectors/",
        NewReportBarrierHasSectorsView.as_view(),
        name="barrier_has_sectors_uuid",
    ),
    path(
        "reports/<uuid:barrier_id>/sectors/",
        NewReportBarrierSectorsView.as_view(),
        name="barrier_sectors_uuid",
    ),
    path(
        "reports/<uuid:barrier_id>/sectors/add/",
        NewReportBarrierSectorsAddView.as_view(),
        name="barrier_add_sectors_uuid",
    ),
    path(
        "reports/<uuid:barrier_id>/sectors/add/all/",
        NewReportBarrierSectorsAddAllView.as_view(),
        name="barrier_add_all_sectors_uuid",
    ),
    path(
        "reports/<uuid:barrier_id>/sectors/remove/",
        NewReportBarrierSectorsRemoveView.as_view(),
        name="barrier_remove_sector_uuid",
    ),
    # About
    path(
        "reports/<uuid:barrier_id>/problem/",
        NewReportBarrierAboutView.as_view(),
        name="barrier_about_uuid",
    ),
    # Summary
    path(
        "reports/<uuid:barrier_id>/summary/",
        NewReportBarrierSummaryView.as_view(),
        name="barrier_summary_uuid",
    ),
    # Categories
    path(
        "reports/<uuid:barrier_id>/categories/",
        NewReportBarrierCategoriesView.as_view(),
        name="barrier_categories_uuid",
    ),
    path(
        "reports/<uuid:barrier_id>/categories/add/",
        NewReportBarrierCategoriesAddView.as_view(),
        name="barrier_categories_add_uuid",
    ),
    path(
        "reports/<uuid:barrier_id>/categories/delete/",
        NewReportBarrierCategoriesDeleteView.as_view(),
        name="barrier_categories_delete_uuid",
    ),
    # Commodities
    path(
        "reports/<uuid:barrier_id>/commodities/",
        NewReportBarrierCommoditiesView.as_view(),
        name="barrier_commodities_uuid",
    ),
    path(
        "reports/<uuid:barrier_id>/check-answers/",
        ReportBarrierAnswersView.as_view(),
        name="report_barrier_answers",
    ),
]
