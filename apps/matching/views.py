"""API views for the Trip Match feature.
Accepts traveler preferences and returns scored, explainable tour recommendations.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.matching.serializers import MatchRequestSerializer, MatchResultItemSerializer
from apps.matching.services import match_tours


class MatchListView(APIView):
    """Public endpoint to score and rank tours based on traveler preferences."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MatchRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        matched_items = match_tours(serializer.validated_data)
        result_serializer = MatchResultItemSerializer(matched_items, many=True)
        return Response({"items": result_serializer.data}, status=status.HTTP_200_OK)
