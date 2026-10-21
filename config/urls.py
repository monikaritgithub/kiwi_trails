"""
Root URL configuration for Kiwi Trails.
Routes API endpoints to each app and serves media files in debug mode.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.catalog.urls")),
    path("api/v1/", include("apps.departures.urls")),
    path("api/v1/", include("apps.coupons.urls")),
    path("api/v1/", include("apps.reviews.urls")),
    path("api/v1/", include("apps.bookings.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
