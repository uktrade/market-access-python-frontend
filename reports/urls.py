from django.urls import path, re_path

from barriers.views.report_barrier import ReportBarrierAnswersView
from reports.location_views import NewReportBarrierLocationMasterView
from reports.report_views import (
    NewReportBarrierAboutView,
    NewReportBarrierCategoriesAddView,
    NewReportBarrierCategoriesDeleteView,
    NewReportBarrierCategoriesView,
    NewReportBarrierCommoditiesView,
    NewReportBarrierHasSectorsView,
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
from reports.views import (
    DeleteReport,
    DraftBarriers,
    NewReport,
    NewReportBarrierAdminAreasView,
    NewReportBarrierCausedByTradingBlocView,
    NewReportBarrierLocationAddAdminAreasView,
    NewReportBarrierLocationHasAdminAreasView,
    NewReportBarrierLocationRemoveAdminAreasView,
    NewReportStartRedirect,
)
from reports.report_barrier_view import (
    ReportBarrierWizardView,
    ReportBarrierVanillaWizardView
)


app_name = "reports"

urlpatterns = [


    #re_path(
    #    r"^report-a-barrier/(?P<step>.+)$",
    #    ReportBarrierWizardView.as_view(url_name="reports:report-barrier-wizard-step"),
    #    name="report-barrier-wizard-step",
    #),
    #re_path(
    #    r"^report-a-barrier/(?P<barrier_id>)/(?P<step>.+)$",
    #    ReportBarrierWizardView.as_view(url_name="reports:report-barrier-wizard-step-existing"),
    #    name="report-barrier-wizard-step-existing",
    #),
    # Two routes into form - one provides a barrier_id (if the draft already exists), one where
    # we make a new 'report' object in the DB

    path(
        "report-a-barrier/",
        ReportBarrierWizardView.as_view(url_name="reports:report-barrier-wizard-step"),
        name="report-barrier-wizard",
    ),
    path(
        "report-a-barrier/draft/<uuid:barrier_id>/",
        ReportBarrierWizardView.as_view(url_name="reports:report-barrier-wizard-step"),
        name="report-barrier-wizard",
    ),
    path(
        "report-a-barrier/<str:step>",
        ReportBarrierWizardView.as_view(url_name="reports:report-barrier-wizard-step"),
        name="report-barrier-wizard-step",
    ),





    path(
        "report-a-barrier-vanilla/",
        ReportBarrierVanillaWizardView.as_view(url_name="reports:report-barrier-vanilla-wizard-step"),
        name="report-barrier-vanilla-wizard",
    ),
    path(
        "report-a-barrier-vanilla/<str:step>",
        ReportBarrierVanillaWizardView.as_view(url_name="reports:report-barrier-vanilla-wizard-step"),
        name="report-barrier-vanilla-wizard-step",
    ),





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
    # Status
    path(
        "reports/new/start/status/",
        NewReportBarrierStatusView.as_view(),
        name="barrier_status",
    ),
    path(
        "reports/<uuid:barrier_id>/status/",
        NewReportBarrierStatusView.as_view(),
        name="barrier_status_uuid",
    ),
    # Location
    path(
        "reports/new/location/",
        NewReportBarrierLocationMasterView.as_view(),
        name="barrier_location",
    ),
    path(
        "reports/<uuid:barrier_id>/location/",
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
        "reports/<uuid:barrier_id>/about/",
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
        "reports/<uuid:barrier_id>/categories/add_first/",
        NewReportBarrierCategoriesAddView.as_view(),
        {"is_main_journey": True},
        name="barrier_categories_add_first_uuid",
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
