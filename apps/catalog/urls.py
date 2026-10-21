"""URL routes for the catalog application.
Maps endpoints for public and admin catalog management.
Follows the Kiwi Trails catalog route specification.
"""

from django.urls import path

from apps.catalog.views import (
    AdminCategoryCreateView,
    AdminFaqCreateView,
    AdminFaqDetailView,
    AdminGuideCreateView,
    AdminGuideUpdateView,
    AdminTourImageCreateView,
    AdminTourImageDeleteView,
    AdminTourListCreateView,
    AdminTourStatusView,
    AdminTourUpdateView,
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
    path(
        "admin/tours",
        AdminTourListCreateView.as_view(),
        name="admin-tour-list-create",
    ),
    path(
        "admin/tours/<int:pk>",
        AdminTourUpdateView.as_view(),
        name="admin-tour-update",
    ),
    path(
        "admin/tours/<int:pk>/status",
        AdminTourStatusView.as_view(),
        name="admin-tour-status",
    ),
    path(
        "admin/tours/<int:pk>/images",
        AdminTourImageCreateView.as_view(),
        name="admin-tour-image-create",
    ),
    path(
        "admin/tour-images/<int:pk>",
        AdminTourImageDeleteView.as_view(),
        name="admin-tour-image-delete",
    ),
    path(
        "admin/tours/<int:pk>/faqs",
        AdminFaqCreateView.as_view(),
        name="admin-faq-create",
    ),
    path(
        "admin/faqs/<int:pk>",
        AdminFaqDetailView.as_view(),
        name="admin-faq-detail",
    ),
    path(
        "admin/guides",
        AdminGuideCreateView.as_view(),
        name="admin-guide-create",
    ),
    path(
        "admin/guides/<int:pk>",
        AdminGuideUpdateView.as_view(),
        name="admin-guide-update",
    ),
    path(
        "admin/categories",
        AdminCategoryCreateView.as_view(),
        name="admin-category-create",
    ),
]
