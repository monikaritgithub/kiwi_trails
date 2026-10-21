"""URL configuration for the departures app.
Routes endpoints for tour departures and calendar views.
Follows the Kiwi Trails departures route specification.
"""

from django.urls import path

from apps.departures.views import (
    AdminDepartureCreateView,
    AdminDepartureStatusView,
    AdminDepartureUpdateView,
    DepartureCalendarView,
    TourDepartureListView,
)

urlpatterns = [
    path(
        "tours/<int:pk>/departures",
        TourDepartureListView.as_view(),
        name="tour-departures",
    ),
    path(
        "departures/calendar",
        DepartureCalendarView.as_view(),
        name="departure-calendar",
    ),
    path(
        "admin/tours/<int:pk>/departures",
        AdminDepartureCreateView.as_view(),
        name="admin-departure-create",
    ),
    path(
        "admin/departures/<int:pk>",
        AdminDepartureUpdateView.as_view(),
        name="admin-departure-update",
    ),
    path(
        "admin/departures/<int:pk>/status",
        AdminDepartureStatusView.as_view(),
        name="admin-departure-status",
    ),
]
