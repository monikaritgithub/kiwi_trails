"""URL configuration for the reviews application.
Routes endpoints for tour review listing creation and admin views.
Follows the Kiwi Trails review endpoint specifications.
"""

from django.urls import path

from apps.reviews.views import (
    AdminReviewListView,
    ReviewCreateView,
    TourReviewListView,
)

urlpatterns = [
    path(
        "tours/<int:tour_id>/reviews",
        TourReviewListView.as_view(),
        name="tour-review-list",
    ),
    path(
        "reviews",
        ReviewCreateView.as_view(),
        name="review-create",
    ),
    path(
        "admin/reviews",
        AdminReviewListView.as_view(),
        name="admin-review-list",
    ),
]
