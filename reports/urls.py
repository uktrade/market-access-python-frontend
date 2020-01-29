from django.urls import path

from reports.views import (
    DraftBarriers,
    DeleteReport,
    NewReport,
    NewReportBarrierProblemStatusView,
    NewReportBarrierStatusView,
    NewReportBarrierLocationView,
    NewReportBarrierLocationHasAdminAreasView,
    NewReportBarrierLocationAddAdminAreasView,
    NewReportBarrierAdminAreasView,
    NewReportBarrierLocationRemoveAdminAreasView,
    NewReportBarrierHasSectorsView,
    ReportDetail,
    NewReportBarrierSectorsView,
    NewReportBarrierSectorsAddView,
    NewReportBarrierSectorsAddAllView,
    NewReportBarrierSectorsRemoveView,
    NewReportBarrierAboutView
)

app_name = "reports"

urlpatterns = [
    path("reports/", DraftBarriers.as_view(), name="draft_barriers"),
    path("reports/new/", NewReport.as_view(), name="new_report"),
    path("reports/<uuid:barrier_id>/", ReportDetail.as_view(), name="draft_barrier_details_uuid"),
    path("reports/<uuid:report_id>/delete/", DeleteReport.as_view(), name="delete_report"),

    # Problem Status
    path("reports/new/start/", NewReportBarrierProblemStatusView.as_view(), name="barrier_problem_status"),
    path("reports/<uuid:barrier_id>/start/", NewReportBarrierProblemStatusView.as_view(), name="barrier_problem_status_uuid"),
    # Status
    path("reports/new/start/is-resolved/", NewReportBarrierStatusView.as_view(), name="barrier_status"),
    path("reports/<uuid:barrier_id>/is-resolved/", NewReportBarrierStatusView.as_view(), name="barrier_status_uuid"),
    # Location
    path("reports/new/country/", NewReportBarrierLocationView.as_view(), name="barrier_location"),
    path("reports/<uuid:barrier_id>/country/", NewReportBarrierLocationView.as_view(), name="barrier_location_uuid"),
    path("reports/new/country/admin-areas/", NewReportBarrierAdminAreasView.as_view(), name="barrier_admin_areas"),
    path("reports/<uuid:barrier_id>/country/admin-areas/", NewReportBarrierAdminAreasView.as_view(), name="barrier_admin_areas_uuid"),
    path("reports/new/country/has-admin-areas/", NewReportBarrierLocationHasAdminAreasView.as_view(), name="barrier_has_admin_areas"),
    path("reports/<uuid:barrier_id>/country/has-admin-areas/", NewReportBarrierLocationHasAdminAreasView.as_view(), name="barrier_has_admin_areas_uuid"),
    path("reports/new/country/admin-areas/add/", NewReportBarrierLocationAddAdminAreasView.as_view(), name="barrier_add_admin_areas"),
    path("reports/<uuid:barrier_id>/country/admin-areas/add/", NewReportBarrierLocationAddAdminAreasView.as_view(), name="barrier_add_admin_areas_uuid"),
    path("reports/new/country/admin-areas/remove/", NewReportBarrierLocationRemoveAdminAreasView.as_view(), name="barrier_remove_admin_areas"),
    path("reports/<uuid:barrier_id>/country/admin-areas/remove/", NewReportBarrierLocationRemoveAdminAreasView.as_view(), name="barrier_remove_admin_areas_uuid"),
    # Sectors
    path("reports/<uuid:barrier_id>/has-sectors/", NewReportBarrierHasSectorsView.as_view(), name="barrier_has_sectors_uuid"),
    path("reports/<uuid:barrier_id>/sectors/", NewReportBarrierSectorsView.as_view(), name="barrier_sectors_uuid"),
    path("reports/<uuid:barrier_id>/sectors/add/", NewReportBarrierSectorsAddView.as_view(), name="barrier_add_sectors_uuid"),
    path("reports/<uuid:barrier_id>/sectors/add/all/", NewReportBarrierSectorsAddAllView.as_view(), name="barrier_add_all_sectors_uuid"),
    path("reports/<uuid:barrier_id>/sectors/remove/", NewReportBarrierSectorsRemoveView.as_view(), name="barrier_remove_sector_uuid"),
    # About
    path("reports/<uuid:barrier_id>/problem/", NewReportBarrierAboutView.as_view(), name="barrier_about_uuid"),


    # path("barriers/<uuid:id>/interactions/delete-note/<int:note_id>/", BarrierDeleteNote.as_view(), name="delete_note"),

    # app.get( '/:reportId?/start/', controller.start );
    # app.post( '/:reportId?/start/', controller.start );

    # app.get( '/:reportId?/is-resolved/', hasStartFormValues, controller.isResolved );
    # app.post( '/:reportId?/is-resolved/', hasStartFormValues, controller.isResolved );

    # app.get( '/:reportId?/country/', hasStartFormValues, hasResolvedFormValues, controller.country );
    # app.post( '/:reportId?/country/', hasStartFormValues, hasResolvedFormValues, controller.country );

    # app.get( '/:reportId?/country/:countryId/has-admin-areas/', hasStartFormValues, hasResolvedFormValues, controller.hasAdminAreas );
    # app.post( '/:reportId?/country/:countryId/has-admin-areas/', hasStartFormValues, hasResolvedFormValues, controller.hasAdminAreas );

    # app.get( '/:reportId?/country/:countryId/admin-areas/', hasStartFormValues, hasResolvedFormValues, controller.adminAreas.list );
    # app.post( '/:reportId?/country/:countryId/admin-areas/', hasStartFormValues, hasResolvedFormValues, controller.adminAreas.list );

    # app.get( '/:reportId/country/:countryId/admin-areas/add/', controller.adminAreas.add );
    # app.post( '/:reportId/country/:countryId/admin-areas/add/', controller.adminAreas.add );
    # app.post( '/:reportId/country/:countryId/admin-areas/remove/', controller.adminAreas.remove );

    # app.get( '/:reportId/has-sectors/', controller.hasSectors );
    # app.post( '/:reportId/has-sectors/', controller.hasSectors );

    # app.get( '/:reportId/all-sectors/', controller.sectors.allSectors );

    # app.get( '/:reportId/sectors/', controller.sectors.list );
    # app.post( '/:reportId/sectors/', controller.sectors.list );

    # app.get( '/:reportId/sectors/add/all/', controller.sectors.all.add );
    # app.post( '/:reportId/sectors/remove/all/', controller.sectors.all.remove );
    # app.get( '/:reportId/sectors/add/', controller.sectors.add );
    # app.post( '/:reportId/sectors/add/', controller.sectors.add );
    # app.post( '/:reportId/sectors/remove/', controller.sectors.remove );

    # app.get( '/:reportId/problem/', controller.aboutProblem );
    # app.post( '/:reportId/problem/', controller.aboutProblem );

    # app.get( '/:reportId/summary/', controller.summary );
    # app.post( '/:reportId/summary/', controller.summary );

    # app.post( '/:reportId/submit/', controller.submit );
]
