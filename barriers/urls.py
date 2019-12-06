from django.urls import path

from .views import (
    AddABarrier,
    BarrierDetail,
    BarrierEditTitle,
    BarrierEditProduct,
    BarrierEditDescription,
    BarrierEditSource,
    BarrierEditPriority,
    BarrierEditEUExitRelated,
    BarrierEditProblemStatus,
    BarrierEditStatus,
    BarrierAddNote,
    BarrierEditNote,
    BarrierDeleteNote,
    Dashboard,
    FindABarrier,
)

app_name = "barriers"

urlpatterns = [
    path("", Dashboard.as_view(), name="dashboard"),
    path("add-a-barrier/", AddABarrier.as_view(), name="add_a_barrier"),
    path("find-a-barrier/", FindABarrier.as_view(), name="find_a_barrier"),
    path("barriers/<uuid:id>/", BarrierDetail.as_view(), name="barrier_detail"),

    path("barriers/<uuid:id>/edit/title/", BarrierEditTitle.as_view(), name="edit_title"),
    path("barriers/<uuid:id>/edit/product/", BarrierEditProduct.as_view(), name="edit_product"),
    path("barriers/<uuid:id>/edit/description/", BarrierEditDescription.as_view(), name="edit_description"),
    path("barriers/<uuid:id>/edit/source/", BarrierEditSource.as_view(), name="edit_source"),
    path("barriers/<uuid:id>/edit/priority/", BarrierEditPriority.as_view(), name="edit_priority"),
    path("barriers/<uuid:id>/edit/eu-exit-related/", BarrierEditEUExitRelated.as_view(), name="edit_eu_exit_related"),
    path("barriers/<uuid:id>/edit/problem-status/", BarrierEditProblemStatus.as_view(), name="edit_problem_status"),
    path("barriers/<uuid:id>/edit/status/", BarrierEditStatus.as_view(), name="edit_status"),

    path("barriers/<uuid:id>/interactions/add-note/", BarrierAddNote.as_view(), name="add_note"),
    path("barriers/<uuid:id>/interactions/edit-note/<int:note_id>/", BarrierEditNote.as_view(), name="edit_note"),
    path("barriers/<uuid:id>/interactions/delete-note/<int:note_id>/", BarrierDeleteNote.as_view(), name="delete_note"),
]
