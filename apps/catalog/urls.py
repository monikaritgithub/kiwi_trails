"""URL routes for the catalog application.
Maps endpoints for public tour browsing categories and guides.
Follows the Kiwi Trails catalog route specification.
"""

from django.urls import path

from apps.catalog.views import (
    CategoryListView,
    GuideDetailView,
    TourDetailView,
    TourListView,
)

urlpatterns = [
    path("tours", TourListView.as_view(), name="tour-list"),
    path("tours/<int:pk>", TourDetailView.as_view(), name="tour-detail"),
    path("categories", CategoryListView.as_view(), name="category-list"),
    path("guides/<int:pk>", GuideDetailView.as_view(), name="guide-detail"),
]
