"""URL configuration for the coupons app.
Routes endpoints for coupon validation and management.
Follows the Kiwi Trails coupons route specification.
"""

from django.urls import path

from apps.coupons.views import (
    AdminCouponListCreateView,
    AdminCouponUpdateView,
    CouponValidateView,
)

urlpatterns = [
    path(
        "coupons/validate",
        CouponValidateView.as_view(),
        name="coupon-validate",
    ),
    path(
        "admin/coupons",
        AdminCouponListCreateView.as_view(),
        name="admin-coupon-list-create",
    ),
    path(
        "admin/coupons/<int:pk>",
        AdminCouponUpdateView.as_view(),
        name="admin-coupon-update",
    ),
]
