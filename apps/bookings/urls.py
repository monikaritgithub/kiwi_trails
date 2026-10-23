"""URL configuration for the bookings app.
Routes customer price previews, booking creation, and booking history.
"""

from django.urls import path

from apps.bookings.views import (
    BookingCreateView,
    BookingMyListView,
    BookingQuoteView,
)

urlpatterns = [
    path("bookings/quote", BookingQuoteView.as_view(), name="booking-quote"),
    path("bookings/my", BookingMyListView.as_view(), name="booking-my"),
    path("bookings", BookingCreateView.as_view(), name="booking-create"),
]
