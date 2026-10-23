"""URL configuration for the bookings app.
Routes customer price previews and booking creation.
"""

from django.urls import path

from apps.bookings.views import BookingCreateView, BookingQuoteView

urlpatterns = [
    path("bookings/quote", BookingQuoteView.as_view(), name="booking-quote"),
    path("bookings", BookingCreateView.as_view(), name="booking-create"),
]
