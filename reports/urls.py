from django.urls import path

from reports.views import (
    DeleteReport,
    DraftBarriers,
    NewReport,
    NewReportBarrierStatus1,
    NewReportBarrierStatus2,
    NewReportBarrierLocation,
)

app_name = "reports"

urlpatterns = [
    path("reports/", DraftBarriers.as_view(), name="draft_barriers"),
    path("reports/new/", NewReport.as_view(), name="new_report"),
    path("reports/new/start/", NewReportBarrierStatus1.as_view(), name="barrier_problem_status"),
    path("reports/new/start/is-resolved/", NewReportBarrierStatus2.as_view(), name="barrier_status"),
    path("reports/new/start/country/", NewReportBarrierLocation.as_view(), name="barrier_location"),

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

    path("reports/<uuid:report_id>/delete/", DeleteReport.as_view(), name="delete_report"),
    # app.get( '/:reportId/delete/', headerNav( { isDashboard: true } ), dashboardData, controller.delete ),
    # app.post( '/:reportId/delete/', headerNav( { isDashboard: true } ), dashboardData, controller.delete ),

    # // detail must be last route
    # app.get( '/:reportId/', controller.report );
]
