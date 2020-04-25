from django.urls import path, re_path

from .views.archive import ArchiveBarrier, UnarchiveBarrier
from .views.assessments import (
    AddAssessmentDocument,
    AssessmentDetail,
    CancelAssessmentDocument,
    CommercialValueAssessment,
    DeleteAssessmentDocument,
    EconomicAssessment,
    EconomyValueAssessment,
    ExportValueAssessment,
    MarketSizeAssessment,
    NewEconomicAssessment,
)
from .views.companies import (
    BarrierEditCompanies,
    BarrierEditCompaniesSession,
    BarrierRemoveCompany,
    BarrierSearchCompany,
    CompanyDetail,
)
from .views.core import (
    BarrierDetail,
    Dashboard,
    DownloadBarriers,
    FindABarrier,
    WhatIsABarrier,
)
from .views.documents import DownloadDocument
from .views.edit import (
    BarrierEditEndDate,
    BarrierEditTitle,
    BarrierEditProduct,
    BarrierEditSource,
    BarrierEditSummary,
    BarrierEditPriority,
    BarrierEditProblemStatus,
    BarrierEditTags,
    BarrierEditTradeDirection)
from .views.history import BarrierHistory
from .views.location import (
    BarrierEditLocation,
    BarrierEditLocationSession,
    BarrierEditCountry,
    AddAdminArea,
    RemoveAdminArea,
)
from .views.notes import (
    AddNoteDocument,
    CancelNoteDocument,
    DeleteNoteDocument,
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
from .views.statuses import (
    BarrierChangeStatus,
    BarrierEditStatus,
)
from .views.teams import (
    AddTeamMember,
    BarrierTeam,
    DeleteTeamMember,
    SearchTeamMember,
    ChangeOwnerView,
)
from .views.types import (
    AddBarrierType,
    BarrierEditTypes,
    BarrierEditTypesSession,
    BarrierRemoveType,
)
from .views.watchlist import (
    EditWatchlist,
    RemoveWatchlist,
    RenameWatchlist,
    SaveWatchlist,
)
from .views.wto import (
    AddWTODocument,
    CancelWTODocuments,
    DeleteWTODocument,
    EditWTOProfile,
    EditWTOStatus,
)

app_name = "barriers"

urlpatterns = [
    path("", Dashboard.as_view(), name="dashboard"),
    path("find-a-barrier/", FindABarrier.as_view(), name="find_a_barrier"),
    path("find-a-barrier/download/", DownloadBarriers.as_view(), name="download"),
    path("what-is-a-barrier/", WhatIsABarrier.as_view(), name="what_is_a_barrier"),
    path("documents/<uuid:document_id>/download/", DownloadDocument.as_view(), name="download_document"),

    path("watch-list/save/", SaveWatchlist.as_view(), name="save_watchlist"),
    path("watch-list/edit/", EditWatchlist.as_view(), name="edit_watchlist"),
    path("watch-list/rename/<int:index>/", RenameWatchlist.as_view(), name="rename_watchlist"),
    path("watch-list/remove/<int:index>/", RemoveWatchlist.as_view(), name="remove_watchlist"),

    path("barriers/<uuid:barrier_id>/", BarrierDetail.as_view(), name="barrier_detail"),
    re_path("barriers/(?P<barrier_id>[A-Z]-[0-9]{2}-[A-Z0-9]{3})/", BarrierDetail.as_view(), name="barrier_detail_by_code"),

    path("barriers/<uuid:barrier_id>/edit/title/", BarrierEditTitle.as_view(), name="edit_title"),
    path("barriers/<uuid:barrier_id>/edit/product/", BarrierEditProduct.as_view(), name="edit_product"),
    path("barriers/<uuid:barrier_id>/edit/summary/", BarrierEditSummary.as_view(), name="edit_summary"),
    path("barriers/<uuid:barrier_id>/edit/source/", BarrierEditSource.as_view(), name="edit_source"),
    path("barriers/<uuid:barrier_id>/edit/priority/", BarrierEditPriority.as_view(), name="edit_priority"),
    path("barriers/<uuid:barrier_id>/edit/problem-status/", BarrierEditProblemStatus.as_view(), name="edit_problem_status"),
    path("barriers/<uuid:barrier_id>/edit/end-date/", BarrierEditEndDate.as_view(), name="edit_end_date"),
    path("barriers/<uuid:barrier_id>/edit/status/", BarrierEditStatus.as_view(), name="edit_status"),
    path("barriers/<uuid:barrier_id>/edit/tags/", BarrierEditTags.as_view(), name="edit_tags"),
    path("barriers/<uuid:barrier_id>/edit/trade-direction/", BarrierEditTradeDirection.as_view(), name="edit_trade_direction"),
    path("barriers/<uuid:barrier_id>/edit/wto-status/", EditWTOStatus.as_view(), name="edit_wto_status"),
    path("barriers/<uuid:barrier_id>/edit/wto/", EditWTOProfile.as_view(), name="edit_wto_profile"),
    path("barriers/<uuid:barrier_id>/wto/documents/add/", AddWTODocument.as_view(), name="add_wto_document"),
    path("barriers/<uuid:barrier_id>/wto/documents/cancel/", CancelWTODocuments.as_view(), name="cancel_wto_documents"),
    path("barriers/<uuid:barrier_id>/wto/documents/<uuid:document_id>/delete/", DeleteWTODocument.as_view(), name="delete_wto_document"),

    path("barriers/<uuid:barrier_id>/archive/", ArchiveBarrier.as_view(), name="archive"),
    path("barriers/<uuid:barrier_id>/unarchive/", UnarchiveBarrier.as_view(), name="unarchive"),
    path("barriers/<uuid:barrier_id>/history/", BarrierHistory.as_view(), name="history"),

    path("barriers/<uuid:barrier_id>/interactions/add-note/", BarrierAddNote.as_view(), name="add_note"),
    path("barriers/<uuid:barrier_id>/interactions/edit-note/<int:note_id>/", BarrierEditNote.as_view(), name="edit_note"),
    path("barriers/<uuid:barrier_id>/interactions/delete-note/<int:note_id>/", BarrierDeleteNote.as_view(), name="delete_note"),

    path("barriers/<uuid:barrier_id>/interactions/documents/add/", AddNoteDocument.as_view(), name="add_note_document"),
    path("barriers/<uuid:barrier_id>/interactions/documents/cancel/", CancelNoteDocument.as_view(), name="cancel_note_document"),
    path("barriers/<uuid:barrier_id>/interactions/documents/<uuid:document_id>/delete/", DeleteNoteDocument.as_view(), name="delete_note_document"),

    path("barriers/<uuid:barrier_id>/location/", BarrierEditLocationSession.as_view(), name="edit_location_session"),
    path("barriers/<uuid:barrier_id>/location/edit/", BarrierEditLocation.as_view(), name="edit_location"),
    path("barriers/<uuid:barrier_id>/location/country/", BarrierEditCountry.as_view(), name="edit_country"),
    path("barriers/<uuid:barrier_id>/location/add-admin-area/", AddAdminArea.as_view(), name="add_admin_area"),
    path("barriers/<uuid:barrier_id>/location/remove-admin-area/", RemoveAdminArea.as_view(), name="remove_admin_area"),

    path("barriers/<uuid:barrier_id>/status/", BarrierChangeStatus.as_view(), name="change_status"),

    path("barriers/<uuid:barrier_id>/types/", BarrierEditTypesSession.as_view(), name="edit_types_session"),
    path("barriers/<uuid:barrier_id>/types/edit/", BarrierEditTypes.as_view(), name="edit_types"),
    path("barriers/<uuid:barrier_id>/types/remove/", BarrierRemoveType.as_view(), name="remove_type"),
    path("barriers/<uuid:barrier_id>/types/add/", AddBarrierType.as_view(), name="add_type"),

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

    path("barriers/<uuid:barrier_id>/team/", BarrierTeam.as_view(), name="team"),
    path("barriers/<uuid:barrier_id>/team/add/", AddTeamMember.as_view(), name="add_team_member"),
    path("barriers/<uuid:barrier_id>/team/add/search/", SearchTeamMember.as_view(), name="search_team_member"),
    path("barriers/<uuid:barrier_id>/team/delete/<int:team_member_id>", DeleteTeamMember.as_view(), name="delete_team_member"),
    path("barriers/<uuid:barrier_id>/team/change-owner/<int:team_member_id>", ChangeOwnerView.as_view(), name="team_change_owner"),

    path("barriers/<uuid:barrier_id>/assessment/", AssessmentDetail.as_view(), name="assessment_detail"),
    path("barriers/<uuid:barrier_id>/assessment/economic/", EconomicAssessment.as_view(), name="economic_assessment"),
    path("barriers/<uuid:barrier_id>/assessment/economic/new/", NewEconomicAssessment.as_view(), name="new_economic_assessment"),
    path("barriers/<uuid:barrier_id>/assessment/economy-value/", EconomyValueAssessment.as_view(), name="economy_value_assessment"),
    path("barriers/<uuid:barrier_id>/assessment/market-size/", MarketSizeAssessment.as_view(), name="market_size_assessment"),
    path("barriers/<uuid:barrier_id>/assessment/export-value/", ExportValueAssessment.as_view(), name="export_value_assessment"),
    path("barriers/<uuid:barrier_id>/assessment/commercial-value/", CommercialValueAssessment.as_view(), name="commercial_value_assessment"),
    path("barriers/<uuid:barrier_id>/assessment/documents/add/", AddAssessmentDocument.as_view(), name="add_assessment_document"),
    path("barriers/<uuid:barrier_id>/assessment/documents/cancel/", CancelAssessmentDocument.as_view(), name="cancel_assessment_document"),
    path("barriers/<uuid:barrier_id>/assessment/documents/<uuid:document_id>/delete/", DeleteAssessmentDocument.as_view(), name="delete_assessment_document"),
]
