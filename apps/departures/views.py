"""API views for public and admin departure endpoints.
Exposes departure listings calendar views and management operations.
Delegates business logic to the departures services layer.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.permissions import IsAdmin
from apps.departures.serializers import (
    DepartureCalendarItemSerializer,
    DepartureCreateSerializer,
    DepartureSerializer,
    DepartureStatusSerializer,
    DepartureUpdateSerializer,
)
from apps.departures.services import (
    create_departure,
    get_departure_calendar,
    list_tour_departures,
    set_departure_status,
    update_departure,
)


class TourDepartureListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        departures = list_tour_departures(pk, request.user)
        serializer = DepartureSerializer(departures, many=True)
        return Response({"items": serializer.data}, status=status.HTTP_200_OK)


class DepartureCalendarView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        month_str = request.query_params.get("month")
        departures = get_departure_calendar(month_str)
        serializer = DepartureCalendarItemSerializer(departures, many=True)
        return Response(
            {"month": month_str.strip(), "items": serializer.data},
            status=status.HTTP_200_OK,
        )


class AdminDepartureCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        serializer = DepartureCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        departure = create_departure(pk, serializer.validated_data)
        detail_serializer = DepartureSerializer(departure)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)


class AdminDepartureUpdateView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, pk):
        serializer = DepartureUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        departure = update_departure(pk, serializer.validated_data)
        detail_serializer = DepartureSerializer(departure)
        return Response(detail_serializer.data, status=status.HTTP_200_OK)


class AdminDepartureStatusView(APIView):
    permission_classes = [IsAdmin]

    def patch(self, request, pk):
        serializer = DepartureStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        departure = set_departure_status(pk, serializer.validated_data["status"])
        detail_serializer = DepartureSerializer(departure)
        return Response(detail_serializer.data, status=status.HTTP_200_OK)
