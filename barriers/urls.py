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
from .views.assessments.economic import (
    AddEconomicAssessment,
    ArchiveEconomicAssessment,
    EconomicAssessmentDetail,
    EditEconomicAssessmentData,
    EditEconomicAssessmentRating,
)
from .views.assessments.economic_impact import (
    AddEconomicImpactAssessment,
    ArchiveEconomicImpactAssessment,
    EconomicImpactAssessmentDetail,
)
from .views.assessments.resolvability import (
    AddResolvabilityAssessment,
    ArchiveResolvabilityAssessment,
    EditResolvabilityAssessment,
    ResolvabilityAssessmentDetail,
)
from .views.assessments.strategic import (
    AddStrategicAssessment,
    ArchiveStrategicAssessment,
    EditStrategicAssessment,
    StrategicAssessmentDetail,
)
from .views.categories import (
    AddCategory,
    BarrierEditCategories,
    BarrierEditCategoriesSession,
    BarrierRemoveCategory,
)
from .views.commodities import BarrierEditCommodities
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
    WhatIsABarrier,
)
from .views.documents import DownloadDocument
from .views.edit import (
    BarrierEditCausedByTradingBloc,
    BarrierEditEconomicAssessmentEligibility,
    BarrierEditEndDate,
    BarrierEditTitle,
    BarrierEditProduct,
    BarrierEditSource,
    BarrierEditSummary,
    BarrierEditPriority,
    BarrierEditTerm,
    BarrierEditTags,
    BarrierEditTradeDirection,
)
from .views.history import BarrierHistory
from .views.location import (
    BarrierEditLocation,
    BarrierEditLocationSession,
    BarrierEditCountryOrTradingBloc,
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
from .views.public_barriers import (
    PublicBarrierDetail,
    EditPublicEligibility,
    EditPublicTitle,
    EditPublicSummary,
    PublicBarrierListView,
)
from .views.search import (
    DownloadBarriers,
    BarrierSearch,
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
    BarrierTeam,
    DeleteTeamMember,
    SearchTeamMember,
    ChangeOwnerView,
)
from .views.saved_searches import (
    DeleteSavedSearch,
    NewSavedSearch,
    RenameSavedSearch,
    SavedSearchNotifications,
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
    path("search/", BarrierSearch.as_view(), name="search"),
    path("find-a-barrier/", BarrierSearch.as_view(), name="find_a_barrier"),
    path("search/download/", DownloadBarriers.as_view(), name="download"),
    path("what-is-a-barrier/", WhatIsABarrier.as_view(), name="what_is_a_barrier"),
    path("documents/<uuid:document_id>/download/", DownloadDocument.as_view(), name="download_document"),

    path("saved-searches/new/", NewSavedSearch.as_view(), name="new_saved_search"),
    path("saved-searches/<uuid:saved_search_id>/rename/", RenameSavedSearch.as_view(), name="rename_saved_search"),
    path("saved-searches/<uuid:saved_search_id>/delete/", DeleteSavedSearch.as_view(), name="delete_saved_search"),
    path("saved-searches/<uuid:saved_search_id>/notifications/", SavedSearchNotifications.as_view(), name="saved_search_notifications"),
    re_path("saved-searches/(?P<saved_search_id>(my|team)-barriers)/notifications/", SavedSearchNotifications.as_view(), name="saved_search_notifications"),

    path("barriers/<uuid:barrier_id>/", BarrierDetail.as_view(), name="barrier_detail"),
    re_path("barriers/(?P<barrier_id>[A-Z]-[0-9]{2}-[A-Z0-9]{3})/", BarrierDetail.as_view(), name="barrier_detail_by_code"),

    path("barriers/<uuid:barrier_id>/edit/title/", BarrierEditTitle.as_view(), name="edit_title"),
    path("barriers/<uuid:barrier_id>/edit/product/", BarrierEditProduct.as_view(), name="edit_product"),
    path("barriers/<uuid:barrier_id>/edit/summary/", BarrierEditSummary.as_view(), name="edit_summary"),
    path("barriers/<uuid:barrier_id>/edit/source/", BarrierEditSource.as_view(), name="edit_source"),
    path("barriers/<uuid:barrier_id>/edit/priority/", BarrierEditPriority.as_view(), name="edit_priority"),
    path("barriers/<uuid:barrier_id>/edit/term/", BarrierEditTerm.as_view(), name="edit_term"),
    path("barriers/<uuid:barrier_id>/edit/economic-assessment-eligibility/", BarrierEditEconomicAssessmentEligibility.as_view(), name="economic_assessment_eligibility"),
    path("barriers/<uuid:barrier_id>/edit/end-date/", BarrierEditEndDate.as_view(), name="edit_end_date"),
    path("barriers/<uuid:barrier_id>/edit/commodities/", BarrierEditCommodities.as_view(), name="edit_commodities"),
    path("barriers/<uuid:barrier_id>/edit/status/", BarrierEditStatus.as_view(), name="edit_status"),
    path("barriers/<uuid:barrier_id>/edit/tags/", BarrierEditTags.as_view(), name="edit_tags"),
    path("barriers/<uuid:barrier_id>/edit/trade-direction/", BarrierEditTradeDirection.as_view(), name="edit_trade_direction"),
    path("barriers/<uuid:barrier_id>/edit/caused-by-trading-bloc/", BarrierEditCausedByTradingBloc.as_view(), name="edit_caused_by_trading_bloc"),
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
    path("barriers/<uuid:barrier_id>/location/country/", BarrierEditCountryOrTradingBloc.as_view(), name="edit_country"),
    path("barriers/<uuid:barrier_id>/location/add-admin-area/", AddAdminArea.as_view(), name="add_admin_area"),
    path("barriers/<uuid:barrier_id>/location/remove-admin-area/", RemoveAdminArea.as_view(), name="remove_admin_area"),

    path("barriers/<uuid:barrier_id>/status/", BarrierChangeStatus.as_view(), name="change_status"),

    path("barriers/<uuid:barrier_id>/types/", BarrierEditCategoriesSession.as_view(), name="edit_categories_session"),
    path("barriers/<uuid:barrier_id>/types/edit/", BarrierEditCategories.as_view(), name="edit_categories"),
    path("barriers/<uuid:barrier_id>/types/remove/", BarrierRemoveCategory.as_view(), name="remove_category"),
    path("barriers/<uuid:barrier_id>/types/add/", AddCategory.as_view(), name="add_category"),

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

    path("barriers/<uuid:barrier_id>/economic-assessments/add", AddEconomicAssessment.as_view(), name="add_economic_assessment"),
    path("barriers/<uuid:barrier_id>/economic-assessments/add/data", EditEconomicAssessmentData.as_view(), name="add_economic_assessment_data"),
    path("barriers/<uuid:barrier_id>/economic-assessments/<int:assessment_id>/", EconomicAssessmentDetail.as_view(), name="economic_assessment_detail"),
    path("barriers/<uuid:barrier_id>/economic-assessments/<int:assessment_id>/edit/data", EditEconomicAssessmentData.as_view(), name="edit_economic_assessment_data"),
    path("barriers/<uuid:barrier_id>/economic-assessments/<int:assessment_id>/edit/rating", EditEconomicAssessmentRating.as_view(), name="edit_economic_assessment_rating"),
    path("barriers/<uuid:barrier_id>/economic-assessments/<int:assessment_id>/edit/commercial-value", EditCommercialValue.as_view(), name="edit_commercial_value"),
    path("barriers/<uuid:barrier_id>/economic-assessments/<int:assessment_id>/archive", ArchiveEconomicAssessment.as_view(), name="archive_economic_assessment"),

    path("barriers/<uuid:barrier_id>/economic-impact-assessments/add", AddEconomicImpactAssessment.as_view(), name="add_economic_impact_assessment"),
    path("barriers/<uuid:barrier_id>/economic-impact-assessments/<uuid:assessment_id>/", EconomicImpactAssessmentDetail.as_view(), name="economic_impact_assessment_detail"),
    path("barriers/<uuid:barrier_id>/economic-impact-assessments/<uuid:assessment_id>/archive", ArchiveEconomicImpactAssessment.as_view(), name="archive_economic_impact_assessment"),

    path("barriers/<uuid:barrier_id>/resolvability-assessments/add", AddResolvabilityAssessment.as_view(), name="add_resolvability_assessment"),
    path("barriers/<uuid:barrier_id>/resolvability-assessments/<uuid:assessment_id>/", ResolvabilityAssessmentDetail.as_view(), name="resolvability_assessment_detail"),
    path("barriers/<uuid:barrier_id>/resolvability-assessments/<uuid:assessment_id>/edit", EditResolvabilityAssessment.as_view(), name="edit_resolvability_assessment"),
    path("barriers/<uuid:barrier_id>/resolvability-assessments/<uuid:assessment_id>/archive", ArchiveResolvabilityAssessment.as_view(), name="archive_resolvability_assessment"),

    path("barriers/<uuid:barrier_id>/strategic-assessments/add", AddStrategicAssessment.as_view(), name="add_strategic_assessment"),
    path("barriers/<uuid:barrier_id>/strategic-assessments/<uuid:assessment_id>/", StrategicAssessmentDetail.as_view(), name="strategic_assessment_detail"),
    path("barriers/<uuid:barrier_id>/strategic-assessments/<uuid:assessment_id>/edit", EditStrategicAssessment.as_view(), name="edit_strategic_assessment"),
    path("barriers/<uuid:barrier_id>/strategic-assessments/<uuid:assessment_id>/archive", ArchiveStrategicAssessment.as_view(), name="archive_strategic_assessment"),

    path("barriers/<uuid:barrier_id>/public/", PublicBarrierDetail.as_view(), name="public_barrier_detail"),
    path("barriers/<uuid:barrier_id>/public/eligibility/", EditPublicEligibility.as_view(), name="edit_public_eligibility"),
    path("barriers/<uuid:barrier_id>/public/title/", EditPublicTitle.as_view(), name="edit_public_barrier_title"),
    path("barriers/<uuid:barrier_id>/public/summary/", EditPublicSummary.as_view(), name="edit_public_barrier_summary"),

    path("public-barriers/", PublicBarrierListView.as_view(), name="public_barriers")
]
