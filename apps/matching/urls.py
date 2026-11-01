"""URL routing for the matching app."""

from django.urls import path

from apps.matching.views import MatchListView

urlpatterns = [
    path("matches", MatchListView.as_view(), name="match-list-no-slash"),
    path("matches/", MatchListView.as_view(), name="match-list"),
]
