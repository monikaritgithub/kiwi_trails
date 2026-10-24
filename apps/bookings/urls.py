"""URL configuration for the bookings app.
Routes customer quotes, creation, history, and booking details.
"""

from django.urls import path

from apps.bookings.views import (
    BookingCreateView,
    BookingDetailView,
    BookingMyListView,
    BookingQuoteView,
)

urlpatterns = [
    path("bookings/quote", BookingQuoteView.as_view(), name="booking-quote"),
    path("bookings/my", BookingMyListView.as_view(), name="booking-my"),
    path("bookings", BookingCreateView.as_view(), name="booking-create"),
    path(
        "bookings/<int:booking_id>",
        BookingDetailView.as_view(),
        name="booking-detail",
    ),
]
