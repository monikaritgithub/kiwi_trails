"""Views for booking API endpoints.
Handles customer price previews, booking creation, and booking history.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.bookings.serializers import (
    BookingCreateSerializer,
    BookingQuoteSerializer,
    BookingSerializer,
)
from apps.bookings.services import (
    calculate_booking_quote,
    create_booking,
    list_customer_bookings,
)
from apps.core.pagination import ApiPagination
from apps.core.permissions import IsCustomer


class BookingQuoteView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request):
        serializer = BookingQuoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quote = calculate_booking_quote(**serializer.validated_data)
        return Response(quote)


class BookingCreateView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def post(self, request):
        serializer = BookingCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        booking = create_booking(
            user=request.user,
            **serializer.validated_data,
        )

        return Response(
            BookingSerializer(booking).data,
            status=status.HTTP_201_CREATED,
        )


class BookingMyListView(APIView):
    permission_classes = [IsAuthenticated, IsCustomer]

    def get(self, request):
        bookings = list_customer_bookings(
            user=request.user,
            status=request.query_params.get("status"),
        )

        paginator = ApiPagination()
        page = paginator.paginate_queryset(bookings, request, view=self)
        serializer = BookingSerializer(page, many=True)

        return paginator.get_paginated_response(serializer.data)
