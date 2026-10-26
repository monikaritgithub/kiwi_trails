"""URL configuration for the bookings app.
Routes customer booking actions and the administrator booking list.
"""

from django.urls import path

from apps.bookings.views import (
    AdminAttendanceListView,
    AdminAttendanceUpdateView,
    AdminBookingListView,
    AdminBookingStatusView,
    BookingCalendarView,
    BookingCancelView,
    BookingCreateView,
    BookingDetailView,
    BookingInvoiceView,
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
    path(
        "bookings/<int:booking_id>/cancel",
        BookingCancelView.as_view(),
        name="booking-cancel",
    ),
    path(
        "bookings/<int:booking_id>/invoice",
        BookingInvoiceView.as_view(),
        name="booking-invoice",
    ),
    path(
        "bookings/<int:booking_id>/calendar",
        BookingCalendarView.as_view(),
        name="booking-calendar",
    ),
    path(
        "admin/bookings",
        AdminBookingListView.as_view(),
        name="admin-booking-list",
    ),
    path(
        "admin/bookings/<int:booking_id>/status",
        AdminBookingStatusView.as_view(),
        name="admin-booking-status",
    ),
    path(
        "admin/departures/<int:departure_id>/attendance",
        AdminAttendanceListView.as_view(),
        name="admin-attendance-list",
    ),
    path(
        "admin/bookings/<int:booking_id>/attendance",
        AdminAttendanceUpdateView.as_view(),
        name="admin-attendance-update",
    ),
]
