from django.urls import path

from .views.companies import (
    BarrierEditCompanies,
    BarrierEditCompaniesSession,
    BarrierRemoveCompany,
    BarrierSearchCompany,
    CompanyDetail,
)
from .views.core import (
    AddABarrier,
    BarrierDetail,
    Dashboard,
    FindABarrier,
)
from .views.edit import (
    BarrierEditTitle,
    BarrierEditProduct,
    BarrierEditDescription,
    BarrierEditSource,
    BarrierEditPriority,
    BarrierEditEUExitRelated,
    BarrierEditProblemStatus,
    BarrierEditStatus,
)
from .views.location import (
    BarrierEditLocation,
    BarrierEditLocationSession,
    BarrierEditCountry,
    AddAdminArea,
    RemoveAdminArea,
)
from .views.notes import (
    BarrierAddNote,
    BarrierEditNote,
    BarrierDeleteNote,
)
from .views.sectors import (
    BarrierAddAllSectors,
    BarrierAddSectors,
    BarrierEditSectors,
    BarrierEditSectorsSession,
    BarrierRemoveSector,
)

app_name = "barriers"

urlpatterns = [
    path("", Dashboard.as_view(), name="dashboard"),
    path("add-a-barrier/", AddABarrier.as_view(), name="add_a_barrier"),
    path("find-a-barrier/", FindABarrier.as_view(), name="find_a_barrier"),
    # path("find-a-barrier/download/", DownloadBarriers.as_view(), name="download_barriers"),
    # path("what-is-a-barrier/", WhatIsABarrier.as_view(), name="what_is_a_barrier"),

    path("barriers/<uuid:barrier_id>/", BarrierDetail.as_view(), name="barrier_detail"),

    path("barriers/<uuid:barrier_id>/edit/title/", BarrierEditTitle.as_view(), name="edit_title"),
    path("barriers/<uuid:barrier_id>/edit/product/", BarrierEditProduct.as_view(), name="edit_product"),
    path("barriers/<uuid:barrier_id>/edit/description/", BarrierEditDescription.as_view(), name="edit_description"),
    path("barriers/<uuid:barrier_id>/edit/source/", BarrierEditSource.as_view(), name="edit_source"),
    path("barriers/<uuid:barrier_id>/edit/priority/", BarrierEditPriority.as_view(), name="edit_priority"),
    path("barriers/<uuid:barrier_id>/edit/eu-exit-related/", BarrierEditEUExitRelated.as_view(), name="edit_eu_exit_related"),
    path("barriers/<uuid:barrier_id>/edit/problem-status/", BarrierEditProblemStatus.as_view(), name="edit_problem_status"),
    path("barriers/<uuid:barrier_id>/edit/status/", BarrierEditStatus.as_view(), name="edit_status"),

    path("barriers/<uuid:barrier_id>/interactions/add-note/", BarrierAddNote.as_view(), name="add_note"),
    path("barriers/<uuid:barrier_id>/interactions/edit-note/<int:note_id>/", BarrierEditNote.as_view(), name="edit_note"),
    path("barriers/<uuid:barrier_id>/interactions/delete-note/<int:note_id>/", BarrierDeleteNote.as_view(), name="delete_note"),

    # path("barriers/<uuid:id>/interactions/documents/add/", AddDocument.as_view(), name=""),
    # path("barriers/<uuid:id>/interactions/documents/cancel/", CancelDocument.as_view(), name=""),
    # path("barriers/<uuid:id>/interactions/documents/<int:document_id>/delete/", DeleteDocument.as_view(), name=""),

    # path("barriers/<uuid:id>/interactions/notes/<int:note_id>/documents/add/", AddNoteDocument.as_view(), name=""),
    # path("barriers/<uuid:id>/interactions/notes/<int:note_id>/documents/cancel/", CancelNoteDocument.as_view(), name=""),
    # path("barriers/<uuid:id>/interactions/notes/<int:note_id>/documents/<int:document_id>/delete/", DeleteNoteDocument.as_view(), name=""),

    path("barriers/<uuid:barrier_id>/location/", BarrierEditLocationSession.as_view(), name="edit_location_session"),
    path("barriers/<uuid:barrier_id>/location/edit/", BarrierEditLocation.as_view(), name="edit_location"),
    path("barriers/<uuid:barrier_id>/location/country/", BarrierEditCountry.as_view(), name="edit_country"),
    path("barriers/<uuid:barrier_id>/location/add-admin-area/", AddAdminArea.as_view(), name="add_admin_area"),
    path("barriers/<uuid:barrier_id>/location/remove-admin-area/", RemoveAdminArea.as_view(), name="remove_admin_area"),

    # path("barriers/<uuid:id>/status/", BarrierStatus.as_view(), name=""),

    # path("barriers/<uuid:id>/types/", BarrierTypeList.as_view(), name=""),
    # path("barriers/<uuid:id>/types/edit/", EditBarrierType.as_view(), name=""),
    # path("barriers/<uuid:id>/types/remove/", RemoveBarrierType.as_view(), name=""),
    # path("barriers/<uuid:id>/types/new/", NewBarrierType.as_view(), name=""),
    # path("barriers/<uuid:id>/types/add/", AddBarrierType.as_view(), name=""),

    path("barriers/<uuid:barrier_id>/sectors/", BarrierEditSectorsSession.as_view(), name="edit_sectors_session"),
    path("barriers/<uuid:barrier_id>/sectors/edit/", BarrierEditSectors.as_view(), name="edit_sectors"),
    path("barriers/<uuid:barrier_id>/sectors/remove/", BarrierRemoveSector.as_view(), name="remove_sector"),
    path("barriers/<uuid:barrier_id>/sectors/add/", BarrierAddSectors.as_view(), name="add_sectors"),
    path("barriers/<uuid:barrier_id>/sectors/add/all/", BarrierAddAllSectors.as_view(), name="add_all_sectors"),

    path("barriers/<uuid:barrier_id>/companies/", BarrierEditCompaniesSession.as_view(), name="edit_companies_session"),
    path("barriers/<uuid:barrier_id>/companies/edit/", BarrierEditCompanies.as_view(), name="edit_companies"),
    path("barriers/<uuid:barrier_id>/companies/search/", BarrierSearchCompany.as_view(), name="search_company"),
    path("barriers/<uuid:barrier_id>/companies/remove/", BarrierRemoveCompany.as_view(), name="remove_company"),
    path("barriers/<uuid:barrier_id>/companies/<uuid:company_id>/", CompanyDetail.as_view(), name="company_detail"),

    # path("barriers/<uuid:id>/team/", BarrierTeam.as_view(), name=""),
    # path("barriers/<uuid:id>/team/add/", AddBarrierTeam.as_view(), name=""),
    # path("barriers/<uuid:id>/team/add/search/", SearchBarrierTeam.as_view(), name=""),
    # path("barriers/<uuid:id>/team/delete/<int:member_id>", DeleteTeamMember.as_view(), name=""),

    # path("barriers/<uuid:id>/assessment/", BarrierAssessment.as_view(), name=""),
    # path("barriers/<uuid:id>/assessment/economic/", EconomicAssessment.as_view(), name=""),
    # path("barriers/<uuid:id>/assessment/economic/new/", NewEconomicAssessment.as_view(), name=""),
    # path("barriers/<uuid:id>/assessment/economy-value/", EconomyValueAssessment.as_view(), name=""),
    # path("barriers/<uuid:id>/assessment/market-size/", MarketSizeAssessment.as_view(), name=""),
    # path("barriers/<uuid:id>/assessment/export-value/", ExportValueAssessment.as_view(), name=""),
    # path("barriers/<uuid:id>/assessment/commercial-value/", CommercialValueAssessment.as_view(), name=""),
    # path("barriers/<uuid:id>/assessment/documents/add/", AddAssessmentDocument.as_view(), name=""),
    # path("barriers/<uuid:id>/assessment/documents/cancel/", CancelAssessmentDocument.as_view(), name=""),
    # path("barriers/<uuid:id>/assessment/documents/<int:document_id>/delete/", DeleteAssessmentDocument.as_view(), name=""),
]
