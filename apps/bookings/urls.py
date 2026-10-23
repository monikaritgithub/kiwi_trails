"""URL configuration for the bookings app.
Routes customer requests to the booking quote endpoint.
"""

from django.urls import path

from apps.bookings.views import BookingQuoteView

urlpatterns = [
    path("bookings/quote", BookingQuoteView.as_view(), name="booking-quote"),
]
