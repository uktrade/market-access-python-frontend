from django.urls import path

from .views import AddABarrier, BarrierDetail, Dashboard, FindABarrier

app_name = "barriers"

urlpatterns = [
    path("", Dashboard.as_view(), name="dashboard"),
    path("add-a-barrier/", AddABarrier.as_view(), name="add_a_barrier"),
    path("find-a-barrier/", FindABarrier.as_view(), name="find_a_barrier"),
    path("barriers/<uuid:id>/", BarrierDetail.as_view(), name="barrier_detail"),
]
